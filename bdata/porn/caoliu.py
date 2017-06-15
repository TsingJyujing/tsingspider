#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""

from blib.pyurllib import get_soup

# test page url:
# http://cl.4ui.xyz/htm_data/16/1706/2443561.html
# http://cl.4ui.xyz/htm_data/16/1706/2460332.html

caoliu_host = "cl.4ui.xyz"  # 地址可能变化

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
    return [obj.get("src") for obj in page_soup.find(
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


def generate_index_page_url(page_index):
    """

    :param page_index: 索引页面index
    :return: 索引页面的URL
    """
    return "http://%s/thread0806.php?fid=16&search=&page=%d" % (caoliu_host, page_index)


def get_latest_urls(page_index):
    index_soup = get_soup(generate_index_page_url(page_index))
    h3blocks = index_soup.find(name="tbody", attrs={"style": "table-layout:fixed;"}).find_all("h3")
    return_value = dict()
    for h3block in h3blocks:
        try:
            url = "http://%s/%s" % (caoliu_host, h3block.a.get("href"))
            if h3block.a.get("href")[:8] != "htm_data":
                raise Exception("Not a page url")
            if try_to_get_font_color(h3block.a) in ("red", "blue"):
                raise Exception("Not a valid url")
            title = h3block.a.getText()
            return_value[url] = title
        except Exception, err:
            # print err.message
            pass
    # 也可以选择带标题返回
    return return_value.keys()


def try_to_get_font_color(asoup):
    """
    :param asoup:
    :return:
    """
    try:
        return asoup.font.get("color")
    except:
        return "default"
