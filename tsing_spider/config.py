#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan

配置文件，记录各种配置
"""

import os

# 请求超时设置
REQUEST_TIMEOUT = 25

# 浏览器的User Agent参数
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"

# XML解析器
XML_DECODER = 'lxml'

DEBUG_PRINT = True
caoliu_host = "t66y.com"

cookies_path = os.path.expanduser(
    "~/Library/Application Support/Firefox/Profiles/kqatl2m8.default-release/cookies.sqlite"
)


def debug_print(*args, **kwargs):
    """
    Check if print data
    :param args:
    :param kwargs:
    :return:
    """
    if DEBUG_PRINT:
        print(*args, **kwargs)
