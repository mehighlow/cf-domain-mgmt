# *CloudFlare domain management tool*
This script allows manage DNS records that are held in CloudFlare in declarative way.

# *Purpose of the tool:*
1. ####Infrastrucure as code
DNS records are written in declarative way. Easy to parse and to manipulate with data that is
stored in the data structure everybody loves – json(actually dictionary but can be easily transformed into json).

2. ####Team collaboration
No body needs password to your CF account. Everything happens via token access. You can grant rights to your domain
repo config to your SysOps/DevOps/SRE/Admins team

3. ####History of changes

You always knows what changes have been made and what for. So you can easily find records you 
do not need any more and delete them safely.

4. ####Backup
Delete wrong DNS record? DO not remember the IP address has been removed? Everything can be easely found in your git
history.

5. ####Etc

You can set your CI system to execute sript on push commit.
You can set up and run only 'diffs' between config settings.

## *Current Version:*
-  1.0.0

## *Requirements:*
https://github.com/zmgit/pycloudflare-v4, version >= 0.8.4

or
```python
pip install -r requirements.txt
```

## *Usage:*

```python
./cf-domain-mgmt.py -c configs/example.yml -d domain.com, domain2.com
```

## *Warning:*

1. Please, READ, example.yml in config dir!
2. CF api calls are limited to 1200calls/300seconds for free account. Keep this in mind you have lots of domains.