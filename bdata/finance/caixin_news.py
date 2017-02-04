#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan
"""
import re
from blib.pyurllib import get_soup

search_base_dir = "http://search.caixin.com/search/"


def query_urls(from_date, to_date, query_words):
    link_mdl = search_base_dir + "search.jsp?startDate=%s&endDate=%s&keyword=%s&x=0&y=0"
    url = link_mdl % (from_date, to_date, query_words)
    soup = get_soup(url)
    info_urls = []
    while True:
        next_info = soup.find_all(name='a', attrs={'class', 'pageNavBtn2'})[0]
        all_res = soup.find_all(name='div', attrs={'class', 'searchxt'})
        for res in all_res:
            info_urls.append(res.a.attrs['href'])
        next_info = next_info.attrs['href']
        if next_info == "javascript:void();":
            # Last page
            break
        else:
            soup = get_soup(search_base_dir + next_info)
    return info_urls


def read_normal_article(url):
    soup = get_soup(url)
    title = soup.title.get_text()
    ps = soup.find_all('p')
    text = ''
    for p in ps:
        text += p.get_text() + "\n"
    return title, text


def read_blog(url):
    soup = get_soup(url)
    title = soup.title.get_text()
    blog_content = soup.find_all(name='div', attrs={'class', 'blog_content'})
    ps = blog_content[0].find_all('p')
    text = ''
    for p in ps:
        text += p.get_text() + "\n"
    return title, text


def read_page(url, retry_tms=1):
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
