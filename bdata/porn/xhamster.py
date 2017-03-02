#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import os
import re
import string
from blib.list_file_io import write_raw
from bs4 import BeautifulSoup
from blib.pyurllib import urlread2
XML_DECODER = "lxml"


def getSoup(url):
    page_data = urlread2(url)
    return page_data, BeautifulSoup(page_data, XML_DECODER)


def getTitleFromSoup(sp):
    return sp.find('title').text
    #return ",".join(sp.find('title').text.split(',')[:-1])


def downloadImgList(pageID, imgList, homePath):
    mkpath = homePath + "/%d/" % pageID
    try:
        os.makedirs(mkpath)
    except:
        pass
    for imgURL in imgList:
        fn = ".".join(re.findall('[^/\.]+', imgURL)[-2:])
        write_raw("%s%s" % (mkpath, fn), urlread2(imgURL))


def getJumpUrls(page_data):
    res = re.findall("m\.xhamster\.com/movies/\d*?/", page_data)
    jmp_url_list = ["https://" + x for x in set(res)]
    return jmp_url_list


def getCategories(sp):
    res = sp.find('ul', attrs={'class', 'categories_of_video'}).find_all('a')
    categories_of_video = []
    for r in res:
        categories_of_video.append(r.text)
    return categories_of_video


def getRating(sp):
    res = sp.find('div', attrs={'class', 'rating'})
    return string.atof(res.text[:-1])


def getTime(sp):
    try:
        res = sp.find('div', attrs={'class', 'time'})
        time_range = res.text.split(':')
        secs = string.atoi(time_range[0])*60 + string.atoi(time_range[1])
        return secs
    except:
        return 0


def getPreviewImgList(sp):
    res = sp.find('div', attrs={"class": "screenshots_block clearfix", "id": "screenshots_block"})
    res = res.find_all('img')
    return [r.get('src') for r in res]


def getDownloadLink(sp):
    res = sp.find('a', attrs={"class": "download", "id": "video_download"})
    url_download = res.get('href')
    if not url_download[:4] == "https":
        url_download = "https" + url_download[4:]
    return url_download


def getPageID(url):
    res = re.findall("m\.xhamster\.com/movies/\d*?/", url)[0][22:-1]
    return string.atoi(res)


def genURL(page_id):
    return "https://m.xhamster.com/movies/%d/" % page_id
