# *CloudFlare domain management tool*
This script allows manage DNS records that are held in CloudFlare in declarative way.

# *Purpose of the tool:*
#### Play with DNS records:
-  create: *simply add new line like:*
```
- { name: 'newrecord.domain.com', content: '8.8.8.8', type: 'A', ttl: '1', proxy: 'true'  }

```
-  update: *set proxy to 'false'*
```
- { name: 'newrecord.domain.com', content: '8.8.8.8', type: 'A', ttl: '1', proxy: 'false'  }

```
-  detele: *simply delete the line*

#### Infrastrucure as code
DNS records are written in declarative way. Easy to parse and to manipulate with data that is
stored in the data structure everybody loves – json(actually dictionary but can be easily transformed into json).
#### Team collaboration
No body needs password to your CF account. Everything happens via token access. You can grant rights to your domain
repo config to your SysOps/DevOps/SRE/Admins team
#### History of changes
You always knows what changes have been made and what for. So you can easily find records you 
do not need any more and delete them safely.
#### Backup
Delete wrong DNS record? DO not remember the IP address has been removed? Everything can be easely found in your git
history.
#### Quick DDoS protection:
Easy to set all records 'proxy:true' with security level you need.
#### Etc
- You can set your CI system to execute sript on push commit.
- You can set up and run only 'diffs' between config settings.
- No need to set different CF settings in web-based account.

## *Current Version:*
-  v1.0.0

## *Requirements:*
https://github.com/zmgit/pycloudflare-v4, version >= 0.8.4

or
```
pip install -r requirements.txt
```

## *Usage:*

```
./cf-domain-mgmt.py -c configs/example.yml -d domain.com, domain2.com
```

## *Warning:*

1. Please, READ, example.yml in config dir!
2. CF api calls are limited to 1200calls/300seconds for free account. Keep this in mind you have lots of domains.

## *ToDo:*
1. Check the result after changes have been made (one more api call and compare result)
2. Calculate approximate api calls based on number of domains and number of records to warn about limits
3. Generate report
