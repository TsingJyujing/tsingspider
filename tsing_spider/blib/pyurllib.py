#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan

处理超链接以及超链接获取的BeautifulSoup类
"""

import os
import re
import threading
from urllib.request import urlretrieve

import requests
from bs4 import BeautifulSoup

from tsing_spider.config import REQUEST_TIMEOUT, USER_AGENT, XML_DECODER


def http_get(url: str, retry_times: int = 10):
    """
    Get raw data by URL
    :param url:
    :param retry_times:
    :return:
    """
    for i in range(retry_times):
        try:
            return requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers={
                    'User-Agent': USER_AGENT,
                    'Accept': '"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Host': re.findall('://.*?/', url, re.DOTALL)[0][3:-1]
                }
            ).content
        except:
            pass
    raise Exception("Error while reading:" + url)


def http_get_soup(url: str, retry_times: int = 10, xml_decoder: str = XML_DECODER):
    return BeautifulSoup(http_get(url, retry_times), xml_decoder)  # html.parser


def __download_callback(block_download_count: int, block_size: int, file_size: int, display_name: str = "FILE"):
    """
    Display download progress for debugging
    :param block_download_count:
    :param block_size:
    :param file_size:
    :param display_name:
    :return:
    """
    process_percent = block_download_count * block_size * 100.0 / file_size
    print("%f%% of %s" % (process_percent, display_name))


class LiteFileDownloader(threading.Thread):
    """
    Little data download to file
    """

    def __init__(self, image_url, filename):
        threading.Thread.__init__(self)
        self.image_url = image_url
        self.filename = filename
        self.done = 0

    def run(self):
        if not os.path.exists(self.filename):  # 已经下载过了
            data = http_get(url=self.image_url)
            if data is not None:
                with open(self.filename, 'wb') as fid:
                    fid.write(data)


class LiteDataDownloader(threading.Thread):
    """
    Little data download to RAM buffer
    """

    def __init__(self, image_url, tag):
        threading.Thread.__init__(self)
        self.image_url = image_url
        self.data = None
        self.tag = tag

    def run(self):
        self.data = http_get(url=self.image_url)

    def write_file(self, filename):
        if self.data is not None:
            with open(filename, 'wb') as fid:
                fid.write(self.data)


class DownloadTask(threading.Thread):
    """
    Large file download to file
    """

    def __init__(self, src_url, dst_path):
        # type: (str, str) -> DownloadTask
        threading.Thread.__init__(self)
        self.url = src_url
        self.dst = dst_path

    def run(self):
        urlretrieve(
            url=self.url,
            filename=self.dst,
            reporthook=lambda a, b, c: __download_callback(a, b, c, "%s-->%s" % (self.url, self.dst)))


class LazyContent:
    """
    懒加载的GET请求
    """

    def __init__(self, url: str):
        self._url = url
        self.__data = None

    @property
    def content(self):
        """
        正文
        :return:
        """
        if self.__data is None:
            self.__data = requests.get(self._url).content
        return self.__data


class LazySoup(LazyContent):
    """
    懒加载的Soup
    """

    def __init__(self, url: str, parser: str = "html.parser"):
        self.__parser = parser
        LazyContent.__init__(self, url)

    @property
    def soup(self):
        if self.__soup is None:
            self.__soup = BeautifulSoup(self.content, self.__parser)
        return self.__soup
