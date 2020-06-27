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
from typing import List

from bs4 import BeautifulSoup

from tsing_spider.util import LazySoup, process_html_string, try_to_json

log = logging.getLogger(__file__)


class User:

    def __init__(self, name: str, uid: int):
        self.uid = uid
        self.name = name

    @property
    def json(self):
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
    def parse_user(a_tag):
        return User(
            name=process_html_string(a_tag.get_text()),
            uid=User.extract_uid(a_tag.get("href"))
        )

    def __str__(self):
        return "{}({})".format(
            self.name, self.uid
        )

    def __repr__(self):
        return "User({},{})".format(
            repr(self.name),
            repr(self.uid)
        )


class Reply:
    """
    回复某一个楼层的详细信息
    """

    def __init__(self, user_from: User, content: str, tick: str, user_to: User = None):
        self.tick = tick
        self.content = content
        self.user_to = user_to
        self.user_from = user_from

    @property
    def json(self):
        return {
            "user_from": try_to_json(self.user_from),
            "user_to": try_to_json(self.user_to),
            "content": self.content,
            "tick": self.tick,
        }

    @staticmethod
    def parse_reply(item: BeautifulSoup):
        users = []
        for u in item.find_all("a", attrs={"class": "tshuz_at", "target": "_blank"}):
            users.append(
                User(
                    process_html_string(u.get_text()),
                    User.extract_uid(u.get("href"))
                )
            )
        if len(users) < 1:
            raise Exception("Can't find user information")
        content = process_html_string(item.find("span", attrs={"class": "tshuz_cnt_main"}).get_text())
        tick = item.find("div", attrs={"class": "tshuz_time"}).find("span").get("title")

        return Reply(
            users[0],
            content=content,
            tick=tick,
            user_to=users[1] if len(users) >= 2 else None
        )

    @staticmethod
    def parse_replies(search_block: BeautifulSoup):
        if search_block is None:
            return []
        results = []
        replies_li = search_block.find_all("li")
        if replies_li is None:
            return []
        for item in (
                f for f in replies_li
                if f.get("id") is not None and re.match(r"floor_\d+", f.get("id"))
        ):
            try:
                results.append(
                    Reply.parse_reply(item)
                )
            except Exception as _:
                log.error("Error while parsing reply from item:\n {} \ncaused by: \n{}".format(
                    str(item), traceback.format_exc()
                ))
        return results


class Floor:
    def __init__(self, content_text: str, image_list: List[str], author: User, tick: str, replies: List[Reply]):
        self.replies = replies
        self.tick = tick
        self.author = author
        self.image_list = image_list
        self.content_text = content_text

    @property
    def json(self):
        return {
            "replies": [reply.json for reply in self.replies],
            "tick": self.tick,
            "author": self.author.json,
            "image_list": self.image_list,
            "content": self.content_text
        }

    @staticmethod
    def parse_floor(item):
        return Floor(
            image_list=Floor.parse_content_images(item),
            author=Floor.parse_author(item),
            tick=Floor.parse_tick(item),
            replies=Floor.parse_replies(item),
            content_text=Floor.parse_content_text(item),
        )

    @staticmethod
    def parse_replies(item: BeautifulSoup):
        return Reply.parse_replies(
            item.find("div", attrs={"class": "tshuz_reply"})
        )

    @staticmethod
    def parse_author(item: BeautifulSoup):
        return User.parse_user(
            item.find("a", attrs={"class": "xw1"})
        )

    @staticmethod
    def parse_tick(item: BeautifulSoup):
        t_em = [
            x
            for x in item.find_all("em")
            if x.get("id") is not None and re.match(r"authorposton\d+", x.get("id"))
        ][0]

        if t_em.find("span") is not None:
            return t_em.find("span").get("title")
        else:
            return re.findall(r"20[\d:\-\s]+", t_em.get_text())[0]

    @staticmethod
    def parse_content_text(item):
        content = item.find("td", attrs={"class": "t_f"})
        if content is None:
            content = item.find("div", attrs={"class": "t_f"})
        if content is None:
            raise Exception("Can't find content container in item block.")
        # Remove no permission tip and image text tip
        remove_list = content.find_all("div", attrs={"class": "attach_nopermission attach_tips"})
        if remove_list is not None:
            [s.extract() for s in remove_list]
        remove_list = content.find_all("div", attrs={"class": "tip tip_4 aimg_tip"})
        if remove_list is not None:
            [s.extract() for s in remove_list]

        return process_html_string(content.get_text())

    @staticmethod
    def parse_content_images(item: BeautifulSoup):
        return [i.get("file") for i in item.find_all("img") if i.get("file") is not None]


class ForumThreadComment(LazySoup):
    """
    论坛的帖子的任意一页
    """

    def __init__(self, url: str):
        super().__init__(url)
        self._post_list_buffer = None

    @property
    def page_index(self):
        """
        当前是第几页
        :return:
        """
        return int(re.findall(r"-(\d+)-\d+.html", self._url)[0])

    @property
    def is_first_page(self):
        """
        是不是第一页（也就是有正文的一页）
        :return:
        """
        return self.page_index == 1

    @property
    def title(self):
        return self.soup.find("span", attrs={"id": "thread_subject"}).get_text().strip(" \n")

    @property
    def page_count(self):
        """
        获取总页数
        :return:
        """
        try:
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
        except AttributeError as _:
            log.debug("Can't find in some stage, return 1 as page count")
            return 1

    @property
    def floors(self):
        if self._post_list_buffer is None:
            items = [
                item
                for item in self.soup.find(
                    "div", attrs={"id": "postlist", "class": "pl bm"}
                ).find_all("div")
                if item.get("id") is not None and re.match(r"post_\d+", item.get("id"))
            ]
            floors = []
            for i, item in enumerate(items):
                try:
                    if item.find("div", attrs={"class": "locked"}) is None:
                        floors.append(Floor.parse_floor(item))
                    else:
                        log.debug("Floor {} in page {} is locked".format(
                            i + 1, self._url
                        ))
                except Exception as ex:
                    if self.is_first_page and i == 0:
                        raise ex
                    else:
                        log.warning("Error while analysis floor {} in page {}".format(
                            i + 1, self._url
                        ))
            self._post_list_buffer = floors
        return self._post_list_buffer

    @property
    def comments(self) -> List[Floor]:
        if self.is_first_page:
            return self.floors[1:]
        else:
            return self.floors

    @property
    def subject(self) -> Floor:
        if self.is_first_page:
            return self.floors[0]
        else:
            raise Exception("Can't get subject floor while page index is {}".format(self.page_index))


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
        """
        Get some page in this thread
        :param page_index: from 1 to N
        :return:
        """
        url = self._get_sub_page_url(self._url, page_index)
        return ForumThreadComment(url)

    @property
    def all_comments(self):
        comments = self.comments.copy()
        for i in range(1, self.page_count):
            comments += self._get_page(i + 1).comments
        return comments

    @property
    def zone(self):
        title_block = self.soup.find("h1", attrs={"class": "ts"})
        try:
            return re.findall("\\[.*?\\]", title_block.get_text())[0][1:-1]
        except IndexError as _:
            log.debug("There's no zone info from page {}".format(self._url))
            return None
        except Exception as ex:
            log.warning("Error while get the zone of page {} caused by {}".format(
                self._url,
                traceback.format_exc()
            ))
            raise ex

    @property
    def m3u8_video_links(self):
        video_urls = []
        video_blocks = self.soup.find_all("video")
        if video_blocks is not None:
            for video_block in video_blocks:
                if video_block.get("data-high") is not None:
                    video_urls.append(video_block.get("data-high"))
                elif video_block.get("data-normal") is not None:
                    video_urls.append(video_block.get("data-normal"))
        return video_urls

    @property
    def json(self):
        return {
            "_id": self._url,
            "type": "thread",
            "url": self._url,
            "zone": self.zone,
            "title": self.title,
            "subject": self.subject.json,
            "videos": self.m3u8_video_links,
            "comments": [c.json for c in self.all_comments]
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
        def _check_tbody(tb):
            tb_a = tb.find("a", attrs={"class": "s xst"})
            if tb_a is None:
                return False
            style = tb_a.get("style")
            if style is None:
                style_check = True
            else:
                style_check = style.find("bold") < 0
            return  type(tb.get("id")) is str \
                   and tb.get("id").startswith("normalthread_") \
                   and style_check
        # 获取非置顶帖子列表
        return [re.sub(r"-\d+-\d+.html", "-1-1.html", url) for url in (
            "https://{}/{}".format(self.base_host, tb.find("a", attrs={"class": "s xst"}).get("href"))
            for tb in self.soup.find_all("tbody") if _check_tbody(tb)
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
