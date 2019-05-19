#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import json

from tsing_spider.blib import priority_get_from_dict


def get_title(sp):
    return __get_video_data(sp)["videoModel"]["title"]


def get_categories(sp):
    return [c["name"] for c in __get_video_data(sp)["videoModel"]["categories"]]


def get_rating(sp):
    return __get_video_data(sp)["videoModel"]["rating"]["value"]


def get_duration(sp):
    return __get_video_data(sp)["videoModel"]["duration"]


def get_preview_images(sp):
    res = sp.find('div', attrs={"class": "screenshots_block clearfix", "id": "screenshots_block"})
    res = res.find_all('img')
    return [r.get('src') for r in res]


def get_download_link(sp):
    data = __get_video_data(sp)
    return priority_get_from_dict(
        priority_get_from_dict(data["videoModel"]["x-sources"], ['h265', 'h264']),
        [
            "1080p",
            "720p",
            "640p",
            "480p",
            "240p",
            "144p"
        ]
    )["prime"]


def __get_video_data(sp):
    """
    Get basic information from script block
    todo use V8 engine to get result instead of decode with JSON directly
    :param sp:
    :return:
    """
    scripts = [s.get_text() for s in sp.find_all("script") if s.get_text().find("window.initials") >= 0]
    if len(scripts) <= 0:
        raise Exception("Can't find information <script> block")
    else:
        if len(scripts) > 1:
            print("Warning: <script> block after filtered more than 1")
        return json.loads(scripts[0].strip(" \n;").replace("window.initials = ", ""))
