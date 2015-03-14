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
from core.timegate_utils import date_str


class FedoraHandler(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.path_pattern = re.compile("^/fedora/objects/([a-zA-Z0-9\\_\\:\\-]+)/datastreams/([a-zA-Z0-9\\_\\:\\-]+)/content$")
        self.TIMESTAMPFMT = '%Y-%m-%dT%H:%M:%S.%NZ'

    def get_all_mementos(self, uri_r):

        #validation on uri_r
        uri_r = self.fix_url(uri_r)
        logging.debug(uri_r)
        self.validate_url(uri_r)

        #fetch all versions
        dates = self.all_versions(uri_r)
        tuples = [ (uri_r+"?asOfDateTime="+d,d) for d in dates ]
        return tuples

    def get_memento(self, uri_r, req_datetime):
        timestamp = date_str(req_datetime, self.TIMESTAMPFMT)

        #validation on uri_r
        uri_r = self.fix_url(uri_r)
        self.validate_url(uri_r)

        url = uri_r.replace("/content","")

        #try endpoint
        r = requests.get(url,params={ "asOfDateTime":timestamp,"format":"xml" })
        if r.status == 404:
            raise HandlerError("Cannot find expected resource",status=404)

        doc = self.parse_xml(r.text)
        context = doc.xpathNewContext()
        context.xpathRegisterNs("fedora","http://www.fedora.info/definitions/1/0/management/")
        dsCreateDate = context.xpathEval("/fedora:datastreamProfile/fedora:dsCreateDate")[0].content

        return (uri_r+"?asOfDateTime="+dsCreateDate,dsCreateDate)

    def validate_url(self,uri_r):
        #validation on uri_r
        parse_r = urllib2.urlparse.urlparse(uri_r)
        path = parse_r.path
        m = self.path_pattern.match(path)
        if not(m):
            raise HandlerError("Invalid URI-R for fedora handler. Must be url of datastream.")

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
