#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan

处理超链接以及超链接获取的BeautifulSoup类
"""
import os
import re
import sqlite3
import threading
from http.cookiejar import Cookie, CookieJar
from typing import Optional
from urllib.request import urlretrieve
from warnings import warn

import requests
from bs4 import BeautifulSoup

from tsing_spider.config import REQUEST_TIMEOUT, USER_AGENT, XML_DECODER, cookies_path


def _init_cookies(cookie_jar: CookieJar, firefox_cookies_path: str):
    """
    Initialize cookies from firefox
    :param cookie_jar:
    :param firefox_cookies_path:
    :return:
    """
    con = sqlite3.connect(firefox_cookies_path)
    cur = con.cursor()
    cur.execute("SELECT host, path, isSecure, expiry, name, value FROM moz_cookies")
    for item in cur.fetchall():
        c = Cookie(
            0,
            item[4],
            item[5],
            None,
            False,
            item[0],
            item[0].startswith('.'),
            item[0].startswith('.'),
            item[1],
            False,
            item[2],
            item[3],
            item[3] == "",
            None, None, {}
        )
        cookie_jar.set_cookie(c)
    return cookie_jar


def set_cookies(firefox_cookies_path: Optional[str] = None):
    """
    显式设置Cookies
    :param firefox_cookies_path:
    :return:
    """
    if firefox_cookies_path is None:
        firefox_cookies_path = cookies_path
    requests_session.cookies = _init_cookies(CookieJar(), firefox_cookies_path)


requests_session = requests.Session()
try:
    set_cookies()
except:
    warn("Error while loading firefox cookies from: {}, please check it.".format(cookies_path))


def http_get(url: str, retry_times: int = 10):
    """
    Get raw data by URL
    :param url:
    :param retry_times:
    :return:
    """
    for i in range(retry_times):
        try:
            host = re.findall('://.*?/', url, re.DOTALL)[0][3:-1]
            request_info = requests_session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers={
                    'User-Agent': USER_AGENT,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Host': host,
                },
            )
            return request_info.content
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
            self.__data = http_get(self._url)
        return self.__data


class LazySoup(LazyContent):
    """
    懒加载的Soup
    """

    def __init__(self, url: str, parser: str = "html.parser"):
        self.__parser = parser
        self.__soup = None
        LazyContent.__init__(self, url)

    @property
    def soup(self):
        if self.__soup is None:
            self.__soup = BeautifulSoup(self.content, self.__parser)
        return self.__soup
