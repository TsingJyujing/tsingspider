# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 22:44:29 2015

@author: TsingJyujing

基础的文件操作和字符串矩阵、列表的存取
"""
import csv


def write_raw(filename, data):  # 快速存储得到的数据
    f = open(filename, 'wb')
    f.write(data)
    f.close()


def read_raw(filename):  # 快速存储得到的数据
    f = open(filename, 'r')
    data = f.read()
    f.close()
    return data


def write_strlist(filename, str_list):
    f = open(filename, 'w')
    for str_elem in str_list:
        f.write(str_elem + '\n')
    f.close()


def read_strlist(filename):
    f = open(filename, 'r')
    raw_list = f.readlines()
    for index, str_elem in enumerate(raw_list):
        raw_list[index] = str_elem[:-1]
    f.close()
    return raw_list


def read_strmat(filename, division_char):
    csvfile = file(filename)
    reader = csv.reader(csvfile, delimiter=division_char)
    rtn = []
    for x in reader:
        rtn.append(x)
    csvfile.close()
    return rtn


def write_strmat(filename, str_mat, division_char):
    csvfile = file(filename, 'wb')
    writer = csv.writer(csvfile, delimiter=division_char)
    writer.writerows(str_mat)
    csvfile.close()


if __name__ == "__main__":
    print "Usage: from list_file_io import *"
