#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan
"""

import re
import string
from bs4 import BeautifulSoup
from blib.pyurllib import urlread2
XML_DECODER = "lxml"


# Novel

def get_novel_blocks():
    block_head_list = ["dushijiqing", "jiatingluanlun", "yinqijiaohuan",
                       "gudianwuxia", "xiaoyuanchunse", "changpianlianzai",
                       "huangsexiaohua", "qiangjianxilie"]
    block_urls = []
    for block in block_head_list:
        block_urls.append("http://www.88langke.com/se/%s/" % block)
    return block_urls


def get_novel(novel_url):
    data = urlread2(novel_url)
    soup = BeautifulSoup(data, XML_DECODER)
    novel_text = soup.find("tbody").tr.td.getText()
    novel_title = soup.find_all("div", attrs={"class": "layout mt10"})[2].find("font", attrs={"color": "#000"}).getText()
    return novel_title, novel_text


def get_novel_list_count(block_url_head):
    data = urlread2(block_url_head)
    soup = BeautifulSoup(data, XML_DECODER)
    end_page_url = soup.find("div", attrs={"class": "pageNav px19"}).find_all("a")[-1].get("href")
    end_index = string.atoi(re.findall("\d*?.html", end_page_url)[0][:-5])
    return end_index


def get_novel_list(block_url_head, index):
    host = re.findall("http://.*?/", block_url_head)[0][:-1]
    if index != 0:
        block_url_append = "index_%d.html" % (index + 1)
        block_url_head += block_url_append
    data = urlread2(block_url_head)
    soup = BeautifulSoup(data, XML_DECODER)
    url_soup_list = soup.find("ul", attrs={"class": "textList"}).find_all("a")
    novel_url_list = []
    for url_soup in url_soup_list:
        novel_url_list.append(host + url_soup.get("href"))
    return novel_url_list


if __name__ == "__main__":
    # NovelTest
    blocks = get_novel_blocks()
    for block_url in blocks:
        list_page_count = get_novel_list_count(block_url)
        print "Get %d novel lists" % list_page_count
        for i in range(list_page_count):
            url_list = get_novel_list(block_url, i)
            print "Get %d novel urls" % len(url_list)
            for url in url_list:
                novel_title_got, novel_text_got = get_novel(url)
                print "Get novel: ", novel_title_got
                print "Novel basic info:(%d words)" % (len(novel_text_got))
