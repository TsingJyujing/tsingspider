# -*- coding: utf-8 -*-
"""
模块说明：
    这个模块用来放置一些公共的，基础的库，也就是大部分代码都要使用的库
"""


def priority_get_from_dict(d: dict, ks: list):
    for k in ks:
        if k in d:
            return d[k]
    raise Exception("Can't find key in dict: {} not contains in {}".format(",".join(ks), ",".join(d.keys())))
