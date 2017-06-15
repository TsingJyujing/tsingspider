#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan

作用：文字处理，去掉SQL/JSON/文件名敏感的字符，防止一些意外的错误
"""
import re


def get_extesion(uri):
    """
    提取路径中的后缀（你看我都写了些什么鬼）
    :param uri:
    :return:
    """
    return re.findall("\.[^\.]*?$", uri)[-1]


def str_iterator_to_pgsql_array(str_iterator):
    """
    将字符串Iterator转换为PostgreSQL格式的字符串数组
    :param str_iterator:
    :return:
    """
    return "{%s}" % (",".join(['"%s"' % s for s in str_iterator]))


def validation_filename(title):  #
    """
    去除标题中的非法字符 (Windows)/\:*?"<>|
    :param title:
    :return:
    """
    return re.sub(r"[\/\\\:\*\?\"\<\>\|]", "_", title)


def SQL_replace(strin):
    """
    去除SQL敏感的单引号
    """
    return strin.replace("'", "’").replace("\r", "  ").replace("\n", "  ")


def JSON_replace(strin):
    """
    去除JSON敏感的双引号
    """
    return strin.replace("\"", "”").replace("\r", "  ").replace("\n", "  ")


def filename_replace(strin, replace_string="_"):
    """
    去除文件名敏感的字符
    """
    str_deny_list = ["?", "*", "/", "\\", "<", ">", ":", "\"", "|"]
    for str_deny in str_deny_list:
        strin = strin.replace(str_deny, replace_string)
    return strin
