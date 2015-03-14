"""
Handler for fedora commons
"""
__author__ = "Nicolas Franck"

# Mandatory
from core.handler_baseclass import Handler

# For get_memento() date parameter
import datetime
import urllib
import urllib2
import libxml2
import re
import logging
import requests

# For custom errors sent to client
from errors.timegateerrors import HandlerError


class FedoraHandler(Handler):

    def __init__(self):
        Handler.__init__(self)
        # Initialization code here. This part is run only once
        self.path_pattern = re.compile("^/fedora/objects/([a-zA-Z0-9\\_\\:\\-]+)/datastreams/([a-zA-Z0-9\\_\\:\\-]+)/content$")

    # This is the function to implement: return list of tuples: [(uri_m,datetime),..]
    def get_all_mementos(self, uri_r):
        uri_r = self.fix_url(uri_r)
        #validation on uri_r
        parse_r = urllib2.urlparse.urlparse(uri_r)
        path = parse_r.path
        m = self.path_pattern.match(path)
        if not(m):
            raise HandlerError("Invalid URI-R for fedora handler. Must be url of datastream.")

        #fetch all versions
        dates = self.all_versions(uri_r)
        tuples = [ (uri_r+"?asOfDateTime="+d,d) for d in dates ]
        return tuples

    # Implement this function instead to bypass the TimeGate's best Memento selection algorithm.
    # Also, it can be used if the whole list cannot be accessed easily.
    # If both get_all_mementos() and get_memento() are implemented. get_memento() will always be preferred by the TimeGate.
    def get_memento(self, uri_r, req_datetime):
        raise HandlerError("Cannot find expected resource",status=404)

    def fix_url(self,url):
        return urllib.unquote(url).decode('utf8')

    def request(self,url,params={}):
        return requests.get(url, params=params).text

    def parse_xml(self,content):
        return libxml2.parseDoc(content)

    def all_versions(self,ds_url):
        url = ds_url.replace("/content","/history")
        content = self.request(url,{ "format":"xml" })
        doc = self.parse_xml(content)
        context = doc.xpathNewContext()
        context.xpathRegisterNs("fedora","http://www.fedora.info/definitions/1/0/management/")
        return [ d.content for d in context.xpathEval("//fedora:dsCreateDate") ]
