#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan
"""
import re

from tsing_spider.util import http_get_soup

search_base_dir = "http://search.caixin.com/search/"


def query_urls(from_date, to_date, query_words):
    """
    搜索所有的含有query_words的文章超链接
    时间格式：yyyy-mm-dd
    使用样例：query_urls('2016-09-01', '2016-09-30', '英镑')
    """
    link_mdl = search_base_dir + "search.jsp?startDate=%s&endDate=%s&keyword=%s&x=0&y=0"
    url = link_mdl % (from_date, to_date, query_words)
    soup = http_get_soup(url)
    info_urls = []
    while True:
        next_info = soup.find_all(name='a', attrs={'class', 'pageNavBtn2'})[0]
        all_res = soup.find_all(name='div', attrs={'class', 'searchxt'})
        for res in all_res:
            info_urls.append(res.a.attrs['href'])
        next_info = next_info.attrs['href']
        if next_info == "javascript:void();":
            break  # Last page
        else:
            soup = http_get_soup(search_base_dir + next_info)
    return info_urls


def read_normal_article(url):
    """
    读取一般的文章
    使用样例：read_normal_article('http://international.caixin.com/2017-01-01/101032527.html')
    请勿直接使用这个函数
    """
    soup = http_get_soup(url)
    title = soup.title.get_text()
    ps = soup.find_all('p')
    text = ''
    for p in ps:
        text += p.get_text() + "\n"
    return title, text


def read_blog(url):
    """
    读取一般的文章
    使用样例：read_blog('http://zhang-ming.blog.caixin.com/archives/157115')
    请勿直接使用这个函数
    """
    soup = http_get_soup(url)
    title = soup.title.get_text()
    blog_content = soup.find_all(name='div', attrs={'class', 'blog_content'})
    ps = blog_content[0].find_all('p')
    text = ''
    for p in ps:
        text += p.get_text() + "\n"
    return title, text


def read_page(url, retry_tms=1):
    """
    根据URL判断类型并且读取相应的内容
    使用样例：read_page('http://zhang-ming.blog.caixin.com/archives/157115')
    请使用这个函数，注意出错时会抛出异常，请及时处理
    """
    is_blog = re.findall('blog\.caixin\.com', url)
    is_blog = len(is_blog) > 0
    for i in range(retry_tms):
        if is_blog:
            try:
                return read_blog(url)
            except:
                try:
                    return read_normal_article(url)
                except:
                    pass
        else:
            try:
                return read_normal_article(url)
            except:
                pass
    raise Exception("Error while reading the page")
