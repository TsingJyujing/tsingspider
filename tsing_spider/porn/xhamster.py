#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import json
import logging
import re
from urllib.parse import quote

from tsing_spider.util import LazySoup
from tsing_spider.util import priority_get_from_dict

log = logging.getLogger(__file__)


class BaseXhamsterIndex(LazySoup):

    @property
    def videos(self):
        return [XhamsterVideo(url) for url in self.video_urls]

    @property
    def video_urls(self):
        return [
            div.find("a", attrs={"class": "video-thumb__image-container role-pop thumb-image-container"}).get("href")
            for div in self.soup.find_all("div")
            if div.get("data-video-id") is not None
        ]

    @property
    def page_count(self):
        return max(
            int(s.get("data-page"))
            for s in self.soup.find_all("a", attrs={"class": "xh-paginator-button"})
            if s.get("data-page") is not None
        )


class XhamsterIndex(BaseXhamsterIndex):
    def __init__(self, index: int):
        if index == 1:
            super().__init__("https://xhamster.com/")
        elif index > 1:
            super().__init__("https://xhamster.com/{}".format(index))
        else:
            raise ValueError("Index value error, should be a positive integer but get {}".format(index))


class XhamsterSearch(BaseXhamsterIndex):
    def __init__(self, query: str, index: int = 1):
        url = "https://xhamster.com/search/{}".format(quote(query))
        if index >= 2:
            url += "?page={}".format(index)
        super().__init__(url)


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
            script = repr(self.soup.find("script", attrs={"id": "initials-script"}))
            self.__video_info = json.loads(
                re.findall(r"window.initials=(.*?);<\/script>", script, re.DOTALL)[0]
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
