#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import os
import re
import string
from blib.list_file_io import write_raw
from bs4 import BeautifulSoup
from blib.pyurllib import urlread2

XML_DECODER = "lxml"


def get_data(url):
    return urlread2(url)


def get_mp4_url(page_data):
    return re.findall("html5player.setVideoUrlHigh(.*?);", page_data)[0][2:-2]


def get_title(page_soup):
    return page_soup.find("meta", attrs={"property": "og:title"})['content']


def get_keyword(page_soup):
    return page_soup.find("meta", attrs={"name": "keywords"})['content'].split(",")
