#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan

配置文件，记录各种配置
"""

# 请求超时设置
REQUEST_TIMEOUT = 25

# 浏览器的User Agent参数
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " + \
             "AppleWebKit/537.36 (KHTML, like Gecko) " + \
             "Chrome/42.0.2311.135 " + \
             "Safari/537.36 " + \
             "Edge/12.10240"

# XML解析器
XML_DECODER = 'lxml'

DEBUG_PRINT = True
caoliu_host = "t66y.com"


def debug_print(*args, **kwargs):
    """
    Check if print data
    :param args:
    :param kwargs:
    :return:
    """
    if DEBUG_PRINT:
        print(*args, **kwargs)
