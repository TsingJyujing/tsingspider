# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 14:27:54 2015
@author: TsingJyujing
"""


def list_unique(seq, excludes=[]):  # 删除List中的冗余元素
    seen = set(excludes)  # seen是曾经出现的元素集合   
    return [x for x in seq if x not in seen and not seen.add(x)]


def list_union(seq1, seq2):  # 求并集
    return list(set(seq1).union(set(seq2)))


def list_intersection(seq1, seq2):  # 求交集
    # 另一个可用的代码： return([val for val in seq1 if val in seq2])
    return list(set(seq1).intersection(set(seq2)))


def list_difference(seq1, seq2):  # seq2中有而seq1中没有的差集
    return list(set(seq2).difference(set(seq1)))


def list_double_difference(seq1, seq2):  # 求差集的并集
    return list_unique((list_difference(seq1, seq2)) + (list_difference(seq2, seq1)))


if __name__ == "__main__":
    print("Library Usage: from list_operation import *")
