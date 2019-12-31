#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""

import logging
import re
from typing import List, Optional, Union
from urllib.parse import urljoin

from tsing_spider.util import LazySoup

log = logging.getLogger(__file__)


class XVideoIndexPage(LazySoup):
    def __init__(self, index: int, base_host: str = "www.xvideos.com"):
        assert 0 <= index <= 19999, "index out of range"
        self._new_index = index
        base = "https://{}/".format(base_host)
        if index == 0:
            url = base
        else:
            url = urljoin(base, "new/{}".format(self._new_index))
        self._video_id_list: Optional[List[str]] = None
        LazySoup.__init__(self, url)

    @property
    def video_id_list(self) -> List[str]:
        if self._video_id_list is None:
            self._video_id_list = [
                s["data-id"]
                for s in self.soup.find(
                    "div",
                    attrs={"class": "mozaique"}
                ).find_all(
                    "div",
                    attrs={"class": "thumb-block"}
                )
            ]
        return self._video_id_list

    @property
    def url(self):
        return self._url


class XVideosVideoPage(LazySoup):
    def __init__(self, relative_uri: str = None, video_id: Union[int, str] = None, base_host: str = "www.xvideos.com"):
        if relative_uri is None and video_id is None:
            raise Exception("relative_uri or video_id at least input one!")
        if video_id is not None:
            self.video_id = video_id
            self.relative_uri = "/video{}/".format(video_id)
        else:
            self.video_id = relative_uri.strip("/").split("/")[0]
            self.relative_uri = relative_uri
        self._title: Optional[str] = None
        self._duration: Optional[int] = None
        self._size: Optional[dict] = None
        self._categories: Optional[List[str]] = None
        self._video_link: Optional[str] = None
        self._preview_images: Optional[List[str]] = None
        LazySoup.__init__(self, urljoin("https://" + base_host, self.relative_uri))

    def get_meta(self, meta_property: str):
        return self.soup.find("meta", attrs={"property": meta_property})['content']

    @property
    def title(self):
        if self._title is None:
            self._title = self.get_meta("og:title")
        return self._title

    @property
    def duration(self):
        if self._duration is None:
            self._duration = int(self.get_meta("og:duration"))
        return self._duration

    @property
    def size(self):
        if self._size is None:
            self._size = {
                "width": int(self.get_meta("og:video:width")),
                "height": int(self.get_meta("og:video:height")),
            }
        return self._size

    @property
    def categories(self):
        if self._categories is None:
            self._categories = self.soup.find("meta", attrs={"name": "keywords"})['content'].split(",")
        return self._categories

    @property
    def video_link(self):
        if self._video_link is None:
            self._video_link = re.findall(r"html5player\.setVideoUrlHigh\('(.*?)'\);", str(self.soup))[0]
        return self._video_link

    @property
    def preview_images(self):
        if self._preview_images is None:
            preview_image_base = re.findall(r"html5player\.setThumbUrl\('(.*?)\.\d+\.jpg'\);", str(self.soup))[0]
            self._preview_images = ["{}.{}.jpg".format(preview_image_base, i + 1) for i in range(30)]
        return self._preview_images

    @property
    def url(self):
        return self._url
