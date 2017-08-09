#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import re
from bs4 import BeautifulSoup
from blib.pyurllib import urlread2, CreateDownloadTask
from blib.str_util import validation_filename

XML_DECODER = "lxml"


def get_data(url):
    return urlread2(url)


def get_soup(url):
    return BeautifulSoup(urlread2(url), XML_DECODER)


def get_data_soup(url):
    data = get_data(url)
    return data, BeautifulSoup(data, XML_DECODER)


def get_mp4_url(page_data):
    return re.findall(r"html5player\.setVideoUrlHigh(.*?);", page_data)[0][2:-2]


def get_title(page_soup):
    return page_soup.find("meta", attrs={"property": "og:title"})['content']


def get_keyword(page_soup):
    return page_soup.find("meta", attrs={"name": "keywords"})['content'].split(",")


def get_download_task(url, save_path):
    page_data = get_data(url)
    page_soup = BeautifulSoup(page_data, XML_DECODER)
    mp4url = get_mp4_url(page_data)
    title = get_title(page_soup)
    save_filename = save_path + validation_filename(title) + ".mp4"
    return CreateDownloadTask(mp4url, save_filename)


def auto_process_urls(urls, save_path):
    process_list = list()
    for url in urls:
        try:
            download_thread = get_download_task(url, save_path)
            process_list.append(download_thread)
            download_thread.start()
        except Exception as ex:
            print "Error while appending task:", ex

    for process in process_list:
        process.join()
