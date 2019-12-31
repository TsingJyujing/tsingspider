# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan

使用豆瓣 API 获取的各种数据
"""

import json

from tsing_spider.util import http_get


def get_movie_info(movie_id):
    """
    :param movie_id: Index of Movie
    :return: json string
    """
    return http_get("https://api.douban.com/v2/movie/subject/%s" % movie_id)


def get_movie_json(movie_id):
    """
    :param movie_id: Index of Movie
    :return: json structure
    """
    return json.loads(get_movie_info(movie_id))


def get_book_info(book_id):
    """
    :param book_id: Index of book
    :return: json string
    """
    return http_get("https://api.douban.com/v2/book/%s" % book_id)


def get_book_json(book_id):
    """
    :param book_id: Index of book
    :return: json structure
    """
    return json.loads(get_book_info(book_id))
