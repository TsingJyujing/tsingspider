# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan
"""

from tsing_spider.util import http_get


def get_mail_data(id):
    """
    :param id: Index of mail (up to 22456)
    :return: email text
    """
    return http_get("https://wikileaks.org/dnc-emails//get/%d" % id)
