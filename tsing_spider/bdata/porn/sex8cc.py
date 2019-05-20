#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2019-03-29
@author: Yuan Yi fan
"""

import re
import datetime

from tsing_spider.blib.pyurllib import LazySoup


class ForumThread(LazySoup):
    """
    论坛的帖子
    """

    def __init__(self, url: str):
        super().__init__(url)

    @property
    def title(self):
        return self.soup.find("span", attrs={"id": "thread_subject"}).get_text()

    @property
    def zone(self):
        title_block = self.soup.find("h1", attrs={"class": "ts"})
        if title_block.find("a") is None:
            return re.findall("\\[.*?\\]", title_block.get_text())[0][1:-1]
        else:
            return title_block.find("a").get_text().replace("[", "").replace("]", "")

    @property
    def author(self):
        author_block = self.soup.find(
            "a", attrs={"class": "xw1", "target": "_blank"})
        return {
            "name": author_block.get_text(),
            "url": author_block.get("href")
        }

    @property
    def last_edit_time(self):
        time_str = re.findall(
            "201[\\d\\-\\s\\:]+\d", self.soup.find("i", attrs={"class": "pstatus"}).get_text())[0]
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")

    @property
    def _content_info(self):
        # self.soup.find("div", attrs={"class": "t_f"})
        return self.soup.find("div", attrs={"class": "pcb"})

    @property
    def content_kv_info(self):
        kvs = []
        for line in self._content_info.get_text().replace("\r", "").split("\n"):
            if line.find("】：") >= 0:
                try:
                    kvs.append({
                        "key": re.findall("【.*?】", line)[0][1:-1],
                        "value": re.findall("】：.*", line)[0][2:],
                    })
                except:
                    pass
        return kvs

    @property
    def image_list(self):
        return [img.get("file") for img in self._content_info.find_all("img") if img.get("file") is not None]

    def create_document(self):
        return {
            "_id": self._url,
            "type": "thread",
            "url": self._url,
            "info": self.content_kv_info,
            "text": self._content_info.get_text(),
            "images": self.image_list,
            "author": self.author,
            "zone": self.zone,
            "title": self.title,
            "last_edit": str(self.last_edit_time)
        }


class ForumPage(LazySoup):
    """
    板块中某一页
    """

    def __init__(self, forum_id: int, page_id: int, base_host: str = "sex8.cc"):
        self.page_id = page_id
        self.forum_id = forum_id
        self.base_host = base_host
        LazySoup.__init__(self, self.url)

    @property
    def url(self, protocol: str = "http") -> str:
        return "{}://{}/forum-{}-{}.html".format(
            protocol,
            self.base_host,
            self.forum_id,
            self.page_id
        )

    @property
    def page_count(self) -> int:
        # 获取页面计数
        raw_info = self.soup.find("span", attrs={"id": "fd_page_bottom"}).find(
            "label").find("span").get("title")
        return int(re.findall("\\d+", raw_info, re.DOTALL)[0])

    @property
    def thread_list_url(self):
        # 获取非置顶帖子列表
        return ["http://{}/{}".format(self.base_host, tb.find("a").get("href")) for tb in self.soup.find(
            "table",
            attrs={"id": "threadlisttableid"}
        ).find_all(
            "tbody"
        ) if tb.get("id") is not None and tb.get("id").startswith("normal")]

    @property
    def thread_list(self):
        return [ForumThread(url) for url in self.thread_list_url]


class Forum:
    """
    板块信息
    """

    def __init__(self, forum_id: int, base_host: str = "sex8.cc"):
        self.__forum_id = forum_id
        self.__base_host = base_host
        self.__first_page = self.get_forum_page(1)

    def get_forum_page(self, page_id: int) -> ForumPage:
        """
        获取某一页
        :param page_id:
        :return:
        """
        return ForumPage(self.__forum_id, page_id, self.__base_host)

    def get_page_count(self) -> int:
        """
        获取页数
        :return:
        """
        return self.__first_page.page_count

    def get_pages(self):
        """
        返回所有页面
        :return:
        """
        return (self.get_forum_page(i + 1) for i in range(self.get_page_count()))


class ForumGroup(LazySoup):
    """
    板块组
    """

    def __init__(self, gid: int):
        super().__init__("http://sex8.cc/forum.php?gid=%d" % gid)

    @property
    def forums_ids(self):
        return [int(a.get("href")[6:-7]) for a in self.soup.find_all("a") if
                a.get("href") is not None and a.get("href").startswith("forum-") and a.get("href").endswith("-1.html")]


def __fids():
    # 散碎的FID
    fid = [110, 436, 437, 438, 34, 440, 32, 444, 415, 447, 448, 449, 450]
    for gid in [739, 696, 740]:
        for f in ForumGroup(gid).forums_ids:
            fid.append(f)
    return set(fid)

