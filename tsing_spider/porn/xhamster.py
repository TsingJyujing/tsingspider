#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import json
import logging
import re

from tsing_spider.util import LazySoup
from tsing_spider.util import priority_get_from_dict

log = logging.getLogger(__file__)


class XhamsterIndex(LazySoup):

    def __init__(self, url: str):
        super().__init__(url)

    @property
    def videos(self):
        return [XhamsterVideo(url) for url in self.video_urls]

    @property
    def video_urls(self):
        return [
            div.find("a", attrs={"class": "video-thumb__image-container thumb-image-container"}).get("href")
            for div in self.soup.find_all("div", attrs={"class": "thumb-list__item video-thumb video-thumb--dated"})
        ]


class XhamsterVideo(LazySoup):
    """
    Xhamster页面解析器
    """

    def __init__(self, url: str):
        super().__init__(url)
        self.__video_info = None

    @property
    def video_info(self):
        if self.__video_info is None:
            scripts = [
                s.get_text()
                for s in self.soup.find_all("script")
                if s.get_text().find("window.initials") >= 0
            ]
            if len(scripts) <= 0:
                raise Exception("Can't find information <script> block")
            elif len(scripts) > 1:
                log.warning("Warning: <script> block after filtered more than 1")

            self.__video_info = json.loads(
                re.findall(r"window.initials\s+=\s+(.*?)\n", scripts[0])[0].strip(" \n;")
            )
        return self.__video_info

    @property
    def title(self):
        return self.video_info["videoModel"]["title"]

    @property
    def categories(self) -> list:
        return [{
            "text": item.get_text().strip(" \n"),
            "link": item.get("href")
        } for item in self.soup.find_all("a", attrs={"class": "categories-container__item"})]

    @property
    def rating(self):
        return self.video_info["videoModel"]["rating"]["value"]

    @property
    def duration(self):
        return self.video_info["videoModel"]["duration"]

    @property
    def download_link(self):
        return priority_get_from_dict(
            self.download_links,
            [
                "1080p",
                "720p",
                "640p",
                "480p",
                "240p",
                "144p"
            ]
        )

    @property
    def download_links(self):
        return self.video_info["videoModel"]["sources"]["mp4"]

    @property
    def preview_image(self):
        return self.video_info["videoModel"]["thumbURL"]

    @property
    def json(self):
        return dict(
            url=self.url,
            title=self.title,
            download_link=self.download_link,
            video_info=self.video_info,
            rating=self.rating,
            categories=self.categories,
        )