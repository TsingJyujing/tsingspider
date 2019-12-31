#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2019-03-29
@author: Yuan Yi fan
"""

import logging
import re
import traceback
from functools import lru_cache

from tsing_spider.util import LazySoup, process_html_string

log = logging.getLogger(__file__)


class User:

    def __init__(self, name: str, uid: int):
        self.uid = uid
        self.name = name

    @property
    def doc(self):
        return dict(
            name=self.name,
            uid=self.uid,
        )

    @staticmethod
    def extract_uid(url: str) -> int:
        res = re.findall(r"space-uid-(\d+).html", url)
        if len(res) > 0:
            return int(res[0])
        res = re.findall(r"uid=(\d+)", url)
        if len(res) > 0:
            return int(res[0])
        raise Exception("Can't find uid in string: {}".format(url))

    @staticmethod
    def extract_user(a_tag):
        return User(
            name=process_html_string(a_tag.get_text()),
            uid=User.extract_uid(a_tag.get("href"))
        )


# fixme 重写获取所有评论的代码，使用页面LRU缓存

class ForumThreadComment(LazySoup):
    """
    论坛的帖子的任意一页
    """

    def __init__(self, url: str):
        super().__init__(url)

    @property
    def title(self):
        return self.soup.find("span", attrs={"id": "thread_subject"}).get_text().strip(" \n")

    @property
    def page_count(self):
        """
        获取总页数
        :return:
        """
        return int(re.findall(
            r"\d+",
            self.soup.find(
                "div", attrs={"class": "pg"}
            ).find(
                "label"
            ).find(
                "span"
            ).get(
                "title"
            ),
            re.DOTALL
        )[0])

    @property
    def _poster_list(self):
        return self.soup.find("div", attrs={"id": "postlist", "class": "pl bm"})


class ForumThread(ForumThreadComment):
    """
    论坛的帖子的第一页
    """

    def __init__(self, url: str):
        super().__init__(self._get_sub_page_url(url, 1))

    @staticmethod
    def _get_sub_page_url(url: str, page_index: int):
        return re.sub(r"-(\d+)-\d+.html", "-{}-1.html".format(page_index), url)

    @lru_cache(maxsize=256)
    def _get_page(self, page_index: int):
        url = self._get_sub_page_url(self._url, page_index)
        return ForumThreadComment(url)

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

    @property
    def zone(self):
        title_block = self.soup.find("h1", attrs={"class": "ts"})
        try:
            return re.findall("\\[.*?\\]", title_block.get_text())[0][1:-1]
        except IndexError as _:
            log.info("Can't find zone info from page {}".format(self._url))
            return None
        except Exception as ex:
            log.error("Error while get the zone of page {} caused by {}".format(
                self._url,
                traceback.format_exc()
            ))
            raise ex

    @property
    def author(self):
        author_block = self.soup.find(
            "a", attrs={"class": "xw1", "target": "_blank"})
        return {
            "name": author_block.get_text(),
            "url": author_block.get("href")
        }

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
            "title": self.title
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
    def url(self, protocol: str = "https") -> str:
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
        tb_list = [tb for tb in self.soup.find_all("tbody") if
                   type(tb.get("id")) is str \
                   and tb.get("id").startswith("normalthread_") \
                   and tb.find("a", attrs={"class": "s xst"}).get("style") is None]
        # 获取非置顶帖子列表
        return [re.sub("-\d+-\d+\.html", "-1-1.html", url) for url in (
            "https://{}/{}".format(self.base_host, tb.find("a", attrs={"class": "s xst"}).get("href")) for tb in tb_list
        )]

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
        super().__init__("https://sex8.cc/forum.php?gid=%d" % gid)

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
