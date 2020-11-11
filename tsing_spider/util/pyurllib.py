#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan

Some wrapper function for http client APIs
"""
import logging
import os
import threading

from bs4 import BeautifulSoup

from tsing_spider.config import (
    get_request_timeout,
    get_xml_decoder,
    get_request_header,
    get_request_session
)

log = logging.getLogger(__file__)


def http_get(url: str, headers: dict = None):
    """
    Get raw data by URL
    :param headers: external headers
    :param url:
    :return:
    """
    log.debug("Trying to get url: {}".format(url))
    response = get_request_session().get(
        url,
        timeout=get_request_timeout(),
        headers=get_request_header(url, headers),
        verify=False,
    )
    response.raise_for_status()
    return response.content


def http_get_soup(url: str):
    """
    Get soup
    :param url:
    :return:
    """
    return BeautifulSoup(http_get(url), get_xml_decoder())  # html.parser


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

    def __init__(self, url: str, filepath: str, chuck_size: int = 81920, headers: dict = None):
        threading.Thread.__init__(self)
        self.url = url
        self.filepath = filepath
        self.chuck_size = chuck_size
        self.downloaded_size = 0
        self.done = False
        self.__headers = get_request_header(self.url, headers)

    def run(self):
        with open(self.filepath, "wb") as fp:
            with get_request_session().get(
                    self.url,
                    stream=True,
                    timeout=get_request_timeout(),
                    headers=self.__headers,
                    verify=False,
            ) as response:
                response.raise_for_status()
                chucks = (chuck for chuck in response.iter_content(chunk_size=self.chuck_size) if chuck)
                for chuck in chucks:
                    self.downloaded_size += len(chuck)
                    fp.write(chuck)
        self.done = True


class LazyContent:
    """
    懒加载的GET请求
    """

    def __init__(self, url: str, headers: dict = None):
        self._url = url
        self.__data = None
        self.__headers = get_request_header(self._url, headers)

    @property
    def content(self):
        """
        Get the content of the request
        :return:
        """
        if not self.is_initialized:
            self.set_content(http_get(self._url, self.__headers))
        return self.__data

    @property
    def is_initialized(self) -> bool:
        return self.__data is not None

    @property
    def url(self) -> str:
        """
        The only safe way to get (can't modify) url
        :return:
        """
        return self._url

    def reset_content(self):
        """
        Reset content for load again
        :return:
        """
        self.__data = None

    def set_content(self, value):
        """
        Set content manually (but not recommended call outside)
        :return:
        """
        self.__data = value


class LazySoup(LazyContent):
    """
    懒加载的Soup
    """

    def __init__(self, url: str, parser: str = None, headers: dict = None):
        self.__parser = parser if parser is not None else get_xml_decoder()
        self.__soup = None
        LazyContent.__init__(self, url, headers)

    @property
    def soup(self):
        if self.__soup is None:
            self.__soup = BeautifulSoup(self.content, self.__parser)
        return self.__soup
