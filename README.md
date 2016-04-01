# CKAN extension for DataGM

Latest CKAN version supported: CKAN 2.5


To enable:

```
ckan.tracking_enabled = True

ckan.plugins = datagm ...
```

It uses the built-in tracking feature, so you'll need to set up a cron job:

```
@hourly /usr/lib/ckan/datagm/bin/paster --plugin=ckan tracking update -c /etc/ckan/datagm/production.ini && /usr/lib/ckan/datagm/bin/paster --plugin=ckan search-index rebuild -r -c /etc/ckan/datagm/production.ini
```

