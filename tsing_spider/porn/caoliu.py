#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""

import logging
import re
import time
from typing import List

from tsing_spider.config import get_caoliu_host
from tsing_spider.util import LazySoup, process_html_string

log = logging.getLogger(__file__)


class CaoliuIndexPage(LazySoup):
    def __init__(self, page_index: int):
        super().__init__(
            "https://%s/thread0806.php?fid=16&search=&page=%d" % (get_caoliu_host(), page_index)
        )

    @staticmethod
    def __get_font_color(asoup):
        """
        :param asoup:
        :return:
        """
        try:
            return asoup.font.get("color")
        except:
            return "default"

    @property
    def threads(self):
        return [CaoliuThread(url) for url in self.thread_urls]

    @property
    def thread_urls(self):
        h3blocks = self.soup.find(name="tbody", attrs={"style": "table-layout:fixed;"}).find_all("h3")
        return_value = []
        for h3block in h3blocks:
            try:
                url = "https://%s/%s" % (get_caoliu_host(), h3block.a.get("href"))
                if h3block.a.get("href")[:8] != "htm_data":
                    raise ValueError("Not a page url")
                if self.__get_font_color(h3block.a) in ("red", "blue"):
                    raise Exception("Not a valid thread url")
                return_value.append(url)
            except:
                pass
        return return_value


class CaoliuThreadComment(LazySoup):
    def __init__(self, url: str):
        super().__init__(url)

    @property
    def content_list(self):
        return [
            s.find(name="div", attrs={"class": "tpc_content"})
            for s in self.soup.find_all("div", attrs={"class": "t t2"})
        ]

    @property
    def comments(self):
        return [
            process_html_string(c.get_text())
            for c in self.content_list
        ]


# Test page for developing: https://t66y.com/htm_data/1912/7/3748347.html

class CaoliuThread(CaoliuThreadComment):
    def __init__(self, url: str, delay:float = 0.0):
        super().__init__(url)
        self._page_buffer = dict()
        self.delay = delay

    @property
    def title(self):
        return self.soup.find("h4").getText()

    @property
    def image_list(self):
        """
        页面中图片的URL
        :return:
        """
        image_list = []
        for obj in self.content_list[0].find_all("img"):
            data_src = obj.get("data-src")
            ess_data = obj.get("ess-data")
            src = obj.get("src")
            image_list.append(ess_data or data_src or src)
        return image_list

    @property
    def comments(self):
        return super().comments[1:]

    @property
    def content_text(self):
        return super().comments[0]

    @property
    def all_page_count(self) -> int:
        page_selector = self.soup.find("a", attrs={"class": "w70"})
        if page_selector is not None:
            return int(
                re.findall(
                    r"\d+/(\d+)",
                    page_selector.find("input").get("value")
                )[0]
            )
        else:
            return 1

    @property
    def all_comments(self) -> List[str]:
        comments = []
        comments += self.comments
        for i in range(2, self.all_page_count + 1):
            time.sleep(self.delay)
            comments += self._page(i).comments
        return comments

    @property
    def tid(self):
        return int(re.findall(r"/(\d+).html", self.url)[0])

    def _get_comment_page_url(self, page_index: int):
        return "https://t66y.com/read.php?tid={}&page={}".format(
            self.tid, page_index
        )

    def _page(self, page_index: int) -> CaoliuThreadComment:
        if page_index not in self._page_buffer:
            self._page_buffer[page_index] = CaoliuThreadComment(
                url=self._get_comment_page_url(page_index)
            )
        return self._page_buffer[page_index]

    @property
    def json(self):
        return dict(
            url=self.url,
            tid=self.tid,
            title=self.title,
            image_list=self.image_list,
            comments=self.all_comments,
            content_text=self.content_text
        )
