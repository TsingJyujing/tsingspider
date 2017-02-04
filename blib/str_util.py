#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan

作用：文字处理，去掉SQL/JSON/文件名敏感的字符，防止一些意外的错误
"""


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
