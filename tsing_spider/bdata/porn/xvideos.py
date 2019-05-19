#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""

import re
import sys
import traceback


def get_download_link(page_soup):
    return re.findall(r"html5player\.setVideoUrlHigh(.*?);", str(page_soup))[0][2:-2]


def get_title(page_soup):
    return page_soup.find("meta", attrs={"property": "og:title"})['content']


def get_categories(page_soup):
    return page_soup.find("meta", attrs={"name": "keywords"})['content'].split(",")


def auto_process_urls(urls, save_path):
    process_list = list()
    for url in urls:
        try:
            download_thread = get_download_task(url, save_path)
            process_list.append(download_thread)
            download_thread.start()
        except:
            print("Error while appending task:" + traceback.format_exc(), file=sys.stderr)

    for process in process_list:
        process.join()
