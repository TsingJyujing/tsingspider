#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan

处理超链接以及超链接获取的BeautifulSoup类
"""
import urllib2
import re
from bs4 import BeautifulSoup

from config import request_timeout, user_agent, XML_decoder


def urlread2(url, retry_times=10):
    for i in range(retry_times):
        try:
            req_header = {
                'User-Agent': user_agent,
                'Accept': '"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Host': re.findall('://.*?/', url, re.DOTALL)[0][3:-1]}
            return urllib2.urlopen(urllib2.Request(url, None, req_header), None, request_timeout).read()
        except:
            pass
    print "Error while reading:", url


def get_soup(url, retry_tms=10):
    for i in range(retry_tms):
        try:
            return BeautifulSoup(urlread2(url), XML_decoder)  # html.parser
        except Exception, e:
            print "Error info:", e
            if e.code == 301:
                return BeautifulSoup("", XML_decoder)
            print "Retrying to get data of %s" % url