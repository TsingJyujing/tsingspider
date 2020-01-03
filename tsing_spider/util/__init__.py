# -*- coding: utf-8 -*-
"""
模块说明：
    这个模块用来放置一些公共的，基础的库，也就是大部分代码都要使用的库
"""

from .pyurllib import http_get, http_get_soup, LazyContent, LazySoup, \
    DownloadTask, LiteDataDownloader, LiteFileDownloader


def priority_get_from_dict(d: dict, ks: list):
    """
    For each element k in ks, trying to find k as a key in d, if found, then return the value
    :param d:
    :param ks:
    :return:
    """
    for k in ks:
        if k in d:
            return d[k]
    raise Exception("Can't find key in dict: {} not contains in {}".format(",".join(ks), ",".join(d.keys())))


def process_html_string(text: str):
    return text.strip(" \n\r")
