#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan

处理超链接以及超链接获取的BeautifulSoup类
"""

import requests

import os

try:
    from urllib.request import urlretrieve
except:
    from urllib import urlretrieve
import re
from bs4 import BeautifulSoup
import threading
from config import request_timeout, user_agent, XML_decoder


def urlread2(url, retry_times=10):
    for i in range(retry_times):
        try:
            return requests.get(
                url,
                timeout=request_timeout,
                headers={
                    'User-Agent': user_agent,
                    'Accept': '"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Host': re.findall('://.*?/', url, re.DOTALL)[0][3:-1]
                }
            ).content
        except:
            pass
    print("Error while reading:" + url)


def get_soup(url, retry_tms=10):
    for i in range(retry_tms):
        try:
            return BeautifulSoup(urlread2(url), XML_decoder)  # html.parser
        except:
            print("Retrying to get data of " + url)
    return BeautifulSoup("", XML_decoder)


def download_callback(block_download_count, block_size, file_size, display_name="/dev/null"):
    process_percent = block_download_count * block_size * 100.0 / file_size
    print("%f%% of %s" % (process_percent, display_name))


class CreateDownloadTask(threading.Thread):
    """
    File download module
    """

    def __init__(self, src_url, dst_path):
        # type: (str, str) -> CreateDownloadTask
        threading.Thread.__init__(self)
        self.url = src_url
        self.dst = dst_path

    def run(self):
        urlretrieve(
            url=self.url,
            filename=self.dst,
            reporthook=lambda a, b, c: download_callback(a, b, c, "%s-->%s" % (self.url, self.dst)))


class LiteFileDownloader(threading.Thread):
    """
    小文件下载线程
    """

    def __init__(self, image_url, filename):
        threading.Thread.__init__(self)
        self.image_url = image_url
        self.filename = filename
        self.done = 0

    def run(self):
        if not os.path.exists(self.filename):  # 已经下载过了
            data = urlread2(url=self.image_url)
            if data is not None:
                with open(self.filename, 'wb') as fid:
                    fid.write(data)


class LiteDataDownloader(threading.Thread):
    """
    小文件下载线程(数据缓存)
    """

    def __init__(self, image_url, tag):
        threading.Thread.__init__(self)
        self.image_url = image_url
        self.data = None
        self.tag = tag

    def run(self):
        self.data = urlread2(url=self.image_url)

    def write_file(self, filename):
        if self.data is not None:
            with open(filename, 'wb') as fid:
                fid.write(self.data)


def downloading_information(block_download_count, block_size, file_size, display_name="/dev/null"):
    process_percent = block_download_count * block_size * 100.0 / file_size
    print("%f%% of %s" % (process_percent, display_name))


class CreateDownloadTask(threading.Thread):
    """
    File download module
    """

    def __init__(self, src_url, dst_path):
        # type: (str, str) -> CreateDownloadTask
        threading.Thread.__init__(self)
        self.url = src_url
        self.dst = dst_path

    def run(self):
        urlretrieve(
            url=self.url,
            filename=self.dst,
            reporthook=lambda a, b, c: download_callback(a, b, c, "%s-->%s" % (self.url, self.dst)))
