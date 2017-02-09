#!/usr/bin/env python
# -*- coding: UTF-8 -*-


__title__ = 'cf-domain-mgmt'
__version__ = '0.2.0'
__author__ = 'm8'
__email__ = 'zmpbox@gmail.com'
__license__ = 'MIT'


import os
import sys
import yaml
import datetime
import logging
import argparse
from pycloudflare_v4 import api

start_time = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')
logger = logging.getLogger(__title__)
logger.setLevel(logging.INFO)
ch = logging.FileHandler('{path}/logs/{appname}-{ts}.log'.format(path=os.getcwd(), appname=__title__, ts=start_time))
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

proxy_record_types = ['A', 'CNAME', 'AAAA']
mx_record_types = ['MX']
cfapi_call_counter = 0


def read_config(config_file):
    """
    Reads config and loads it as a dict.
    :param config_file:
    :return: dict
    """

    logger.debug('Project: {0}'.format(config_file))
    if not config_file:
        logger.critical('The PROJECT config file was not set. Please set PROJECT config file name.')
        print('The PROJECT config file was not set. Please set PROJECT config file name.')
        sys.exit(1)
    with open(config_file, 'r') as f:
        try:
            cfg = yaml.load(f)
            logger.debug(cfg)
        except BaseException as e:
            logger.critical(e)
            raise
    return cfg


def process_domain(domain):

    global cfapi_call_counter

    logger.info(domain)
    cf_current_dns_records = cfapi.dns_records(zones[domain]['id'])
    logger.info(cf_current_dns_records)
    cfapi_call_counter += 1
    logger.info("API # {0}".format(cfapi_call_counter))
    cf_to_delete_dns_records = []
    cf_records = []

    """
    First, a list to delete records is created. All records placed in this list.
    Later all matched records will be removed from this list.
    This function allows us to delete records in config.
    """
    for cf_current_record in cf_current_dns_records:
        cf_to_delete_dns_records.append(str(cf_current_record['id']))
        logger.debug("{0}: {1}".format(str(cf_current_record['id']), str(cf_current_record['name'])))

    # Update proxy state, mx priority and ttl
    for config_dns_record in config['domains'][domain]['records']:
        logger.debug(config_dns_record)
        for cf_dns_record in cf_current_dns_records:
            if str(config_dns_record['type']) == str(cf_dns_record['type']) and str(
                    config_dns_record['name']) == str(cf_dns_record['name']) and str(
                    config_dns_record['content']) == str(cf_dns_record['content']):

                # Delete record from delition list if config record matched CF
                cf_to_delete_dns_records.remove(str(cf_dns_record['id']))
                logger.info("ID {0} removed from deletion list {1}".format(str(cf_dns_record['id']),
                                                                           cf_to_delete_dns_records
                                                                           )
                            )
                logger.info("Updating records: {0} {1} {2}".format(str(config_dns_record['type']),
                                                                   str(config_dns_record['name']),
                                                                   str(config_dns_record['content'])
                                                                   )
                            )

                if str(config_dns_record['type']) in proxy_record_types:
                    logger.info("update {0} record".format(proxy_record_types))
                    logger.info(cfapi.dns_records_update(zone_id=zones[domain]['id'],
                                                         record_id=cf_dns_record['id'],
                                                         proxied=config_dns_record['proxy'],
                                                         ttl=config_dns_record['ttl']
                                                         )
                                )
                    cfapi_call_counter += 1
                    logger.info("API # {0}".format(cfapi_call_counter))
                elif str(config_dns_record['type']) in mx_record_types:
                    logger.info("update MX record")
                    logger.info(cfapi.dns_records_update(zone_id=zones[domain]['id'],
                                                         record_id=cf_dns_record['id'],
                                                         priority=config_dns_record['priority'],
                                                         ttl=config_dns_record['ttl']
                                                         )
                                )
                    cfapi_call_counter += 1
                    logger.info("API # {0}".format(cfapi_call_counter))
                else:
                    logger.info("update other records")
                    logger.info(cfapi.dns_records_update(zone_id=zones[domain]['id'],
                                                         record_id=cf_dns_record['id'],
                                                         ttl=config_dns_record['ttl']
                                                         )
                                )
                    cfapi_call_counter += 1
                    logger.info("API # {0}".format(cfapi_call_counter))

    # Delete all ids in to_delete
    if len(cf_to_delete_dns_records) > 0:
        logger.info("Delete CF records:")
        for del_record_id in cf_to_delete_dns_records:
            logger.info(cfapi.dns_records_delete(zones[domain]['id'], del_record_id))
            cfapi_call_counter += 1
            logger.info("API # {0}".format(cfapi_call_counter))

    # Update current CF settings. This is important due to dns_records_update method called earlier.
    cf_current_dns_records = cfapi.dns_records(zones[domain]['id'])
    cfapi_call_counter += 1
    logger.info("API # {0}".format(cfapi_call_counter))
    logger.info("update CF records")
    logger.info(cf_current_dns_records)

    # Create list of records in custom format to be created in CF
    for cf_dns_record in cf_current_dns_records:
        if str(cf_dns_record['type']) in proxy_record_types:
            record = {'type': str(cf_dns_record['type']),
                      'name': str(cf_dns_record['name']),
                      'content': str(cf_dns_record['content']),
                      'ttl': str(cf_dns_record['ttl']),
                      'proxy': ("{0}".format(cf_dns_record['proxied'])).lower()
                      }
            cf_records.append(record)
        elif str(cf_dns_record['type']) in mx_record_types:
            record = {'type': str(cf_dns_record['type']),
                      'name': str(cf_dns_record['name']),
                      'content': str(cf_dns_record['content']),
                      'ttl': str(cf_dns_record['ttl']),
                      'priority': str(cf_dns_record['priority'])
                      }
            cf_records.append(record)
        else:
            record = {'type': str(cf_dns_record['type']),
                      'name': str(cf_dns_record['name']),
                      'content': str(cf_dns_record['content']),
                      'ttl': str(cf_dns_record['ttl'])
                      }
            cf_records.append(record)

    # Create records in CF if not exist
    # dict in config and record dict comes from cloudflare
    for domain_config_rec in config['domains'][domain]['records']:
        if domain_config_rec not in cf_records:

            if str(domain_config_rec['type']) in proxy_record_types:
                logger.info(cfapi.dns_records_create(zone_id=zones[domain]['id'],
                                                     record_type=domain_config_rec['type'],
                                                     record_name=domain_config_rec['name'],
                                                     record_content=domain_config_rec['content'],
                                                     record_ttl=domain_config_rec['ttl'],
                                                     record_proxied=domain_config_rec['proxy']
                                                     )
                            )
                cfapi_call_counter += 1
                logger.info("API # {0}".format(cfapi_call_counter))
            elif str(domain_config_rec['type']) in mx_record_types:
                logger.info(cfapi.dns_records_create(zone_id=zones[domain]['id'],
                                                     record_type=domain_config_rec['type'],
                                                     record_name=domain_config_rec['name'],
                                                     record_content=domain_config_rec['content'],
                                                     record_ttl=domain_config_rec['ttl'],
                                                     record_priority=domain_config_rec['priority']
                                                     )
                            )
                cfapi_call_counter += 1
                logger.info("API # {0}".format(cfapi_call_counter))
            else:
                logger.info(cfapi.dns_records_create(zone_id=zones[domain]['id'],
                                                     record_type=domain_config_rec['type'],
                                                     record_name=domain_config_rec['name'],
                                                     record_content=domain_config_rec['content'],
                                                     record_ttl=domain_config_rec['ttl']
                                                     )
                            )
                cfapi_call_counter += 1
                logger.info("API # {0}".format(cfapi_call_counter))
            logger.info("CF record {0} created".format(domain_config_rec))
        else:
            logger.info("CF record {0} already exists".format(domain_config_rec))

    # Update CF zone settings:
    for setting_name in config['domains'][domain]['cf_settings']:
        method_name = 'change_{0}_setting'.format(setting_name)
        method = getattr(cfapi, method_name)
        cfapi_call_counter += 1
        logger.info("API # {0}".format(cfapi_call_counter))
        logger.info(method(zones[domain]['id'], config['domains'][domain]['cf_settings'][setting_name]))


if __name__ == '__main__':

    project_config_file = False
    single_domain = False
    domains_to_process = []

    parser = argparse.ArgumentParser(prog=__file__, description='CloudFlare management tool')
    parser.add_argument('-v', '--version', action='version', version='{0}'.format(__version__))
    parser.add_argument('-c', '--config', required=True, help='usage: {0} -c <config_file> [-d <domain>]'.format(__file__))
    parser.add_argument('-d', '--domain', required=False, help='usage: {0} -c <config_file> [-d <domain>]'.format(__file__))

    args = vars(parser.parse_args())

    if len(args) == 0:
        parser.print_help()
        sys.exit()

    if args['config']:
        project_config_file = args['config']

    if args['domain']:
        domains_to_process = args['domain'].split(',')

    config = read_config(config_file=project_config_file)
    cf_email = config['cf_account']['email']
    cf_token = config['cf_account']['token']
    logger.debug("Config: {0}".format(config))
    cfapi = api.CloudFlare(cf_email, cf_token)
    cfapi_call_counter += 1
    logger.info("API # {0}".format(cfapi_call_counter))
    zones = cfapi.get_zones()
    cfapi_call_counter += 1
    logger.info("API # {0}".format(cfapi_call_counter))
    logger.debug("Zones on ths account: {0}".format(zones))

    if len(domains_to_process) == 0:
        for i in config['domains']:
            if i not in domains_to_process:
                domains_to_process.append(i)

    logger.info(domains_to_process)
    number_of_domains = len(domains_to_process)
    logger.info("Total domain in config: {0}".format(number_of_domains))

    for domain_name in domains_to_process:
        process_domain(domain_name)
