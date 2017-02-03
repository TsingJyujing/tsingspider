#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan
"""


def SQL_replace(strin):
    return strin.replace("'", "’").replace("\r", "  ").replace("\n", "  ")


def JSON_replace(strin):
    return strin.replace("\"", "”").replace("\r", "  ").replace("\n", "  ")

def filename_replace(strin, replace_string="_"):
    str_deny_list = ["?", "*", "/", "\\", "<", ">", ":", "\"", "|"]
    for str_deny in str_deny_list:
        strin = strin.replace(str_deny, replace_string)
    return strin
