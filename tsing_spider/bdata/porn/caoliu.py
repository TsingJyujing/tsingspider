#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""

from tsing_spider.blib.pyurllib import http_get_soup
from tsing_spider.config import caoliu_host


def get_page_title(page_soup):
    """
    :param page_soup: 页面数据的Soup
    :return: 标题
    """
    return page_soup.find("h4").getText()


def get_page_images(page_soup):
    """
    :param page_soup: 页面数据的Soup
    :return: List<String> 页面中图片的URL
    """
    return [obj.get("data-src") for obj in page_soup.find(
        name="div", attrs={"class": "tpc_content do_not_catch"}
    ).find_all(
        name="input", attrs={"type": "image"}
    )]


def get_page_text(page_soup):
    """
    :param page_soup: 页面数据的Soup
    :return: String 主题文字
    """
    return page_soup.find(
        name="div", attrs={"class": "tpc_content do_not_catch"}
    ).getText()


def get_latest_urls(page_index):
    index_soup = http_get_soup(__generate_index_page_url(page_index))
    h3blocks = index_soup.find(name="tbody", attrs={"style": "table-layout:fixed;"}).find_all("h3")
    return_value = []
    for h3block in h3blocks:
        try:
            url = "https://%s/%s" % (caoliu_host, h3block.a.get("href"))
            if h3block.a.get("href")[:8] != "htm_data":
                raise Exception("Not a page url")
            if __get_font_color(h3block.a) in ("red", "blue"):
                raise Exception("Not a valid url")
            # title = h3block.a.getText()
            return_value.append(url)
        except:
            pass
    return return_value


def __generate_index_page_url(page_index):
    """
    获取索引页面的URL
    :param page_index: 索引页面index
    :return: 索引页面的URL
    """
    return "https://%s/thread0806.php?fid=16&search=&page=%d" % (caoliu_host, page_index)


def __get_font_color(asoup):
    """
    :param asoup:
    :return:
    """
    try:
        return asoup.font.get("color")
    except:
        return "default"
