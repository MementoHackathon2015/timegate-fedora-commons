# Purpose

Handler class for the [mementoweb timegate](https://github.com/mementoweb/timegate) application. With this handler the timegate can request versions of datastreams in Fedora Commons (version 3). Only content urls of datastreams are supported for the moment.

# Install
- copy handler to timegate:
```
$ cd timegate-fedora-commons
$ cp core/handler/fedora.py /path/to/timegate/core/handler
$ cd /path/to/timegate
```
- set fedora handler as default in conf/config.ini (optional):
```
handler_class =core.handler.fedora.FedoraHandler
```
- start timegate application:
```
$ uwsgi --http :9999 --wsgi-file core/application.py
```

# Use

Suppose you have this link to a datastream:

```
http://fedoraAdmin:fedoraAdmin@localhost:8080/fedora/objects/demo:1/datastreams/lion/content
```

Then this url will supply you all versions of the content:
```
http://localhost:9999/timemap/json/http%3A%2F%2FfedoraAdmin%3AfedoraAdmin%40localhost%3A8080%2Ffedora%2Fobjects%2Fdemo%3A1%2Fdatastreams%2Flion%2Fcontent
```

# Reminders

- Fedora Commons requires authentication. In case of basic authentication you need to supply username and password in the url. For the moment there's is no other way for the timegate handler to access the content in Fedora.
- Only content url for datastreams are supported for the moment
