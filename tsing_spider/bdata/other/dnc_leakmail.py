# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan
"""

from tsing_spider.blib.pyurllib import urlread2


def get_mail_data(id):
    """
    :param id: Index of mail (up to 22456)
    :return: email text
    """
    return urlread2("https://wikileaks.org/dnc-emails//get/%d" % id)
