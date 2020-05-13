"""
Resource Index Info from :
    http://javtorrent.re/
    http://h.javtorrent.re/
But HTTPS is not secure
"""
import datetime
import logging
import re
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from tsing_spider.util import LazySoup

log = logging.getLogger(__file__)

JAV_H_HOST = "h.javtorrent.re"
JAV_H_CATEGORIES = [
    "h-game", "h-anime", "h-manga"
]
JAV_HOST = "javtorrent.re"
JAV_CATEGORIES = [
    "censored", "uncensored", "iv"
]

class JavItem(LazySoup):
    def __init__(self, url: str):
        super().__init__(url)
        self._image_ls = None
        self._torrent_ls = None

    @property
    def _content(self) -> BeautifulSoup:
        return self.soup.find("div", attrs={"id": "content"})

    @property
    def torrent_resid_list(self) -> List[str]:
        result = []
        for block in self._content.find_all("div", attrs={"class": "single-t"}):
            try:
                result.append(re.findall(r"d=(.*?)$", block.find("a").get("href"))[0])
            except Exception as ex:
                log.debug("Failed to parse single-t block", exc_info=ex)
        return result

    @property
    def title(self) -> str:
        return self._content.find("div", attrs={"class": "entry-title"}).get_text()

    @property
    def image_url(self) -> str:
        return urljoin(
            self.url,
            self._content.find("img", attrs={"class": "s-full"}).get("src")
        )

    @property
    def tags(self) -> List[str]:
        tags = []
        for blk in self._content.find_all("a"):
            url = blk.get("href")
            if url is not None and url.startswith("/tag/"):
                tags.append(
                    blk.get_text()
                )
        return tags

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.strptime(
            self._content.find("a", attrs={"class": "s-time"}).get_text(),
            "%Y/%m/%d - %H:%M"
        )

    @property
    def image(self) -> bytes:
        if self._image_ls is None:
            self._image_ls = LazySoup(
                url=self.image_url,
                headers={
                    "Referer": self.url
                }
            )
        return self._image_ls.content

    @property
    def torrents(self) -> List[bytes]:
        if self._torrent_ls is None:
            torrents = []
            for torrent_resid in self.torrent_resid_list:
                torrents.append(LazySoup(
                    url=f"http://jtl.re/d/{torrent_resid}.torrent",
                    headers={
                        "Referer": f"http://1on.re/d.php?d={torrent_resid}"
                    }
                ))
            self._torrent_ls = torrents
        return [
            ls.content
            for ls in self._torrent_ls
        ]

    @property
    def json(self):
        return dict(
            url=self.url,
            title=self.title,
            image_url=self.image_url,
            torrent_resid_list=self.torrent_resid_list,
            tags=self.tags,
            time=self.time.strftime("%Y-%m-%d %H:%M"),
        )


class BaseJavIndex(LazySoup):
    def __init__(self, host: str, category: str, page: int, protocol: str = "http"):
        self.protocol = protocol
        self.host = host
        self.category = category
        self.page = page
        url = f"{protocol}://{host}/category/{category}/page/{page}/"
        super().__init__(url)

    @property
    def items(self):
        result = []
        for blk in self.soup.find("div", attrs={"class": "base"}).find_all("div"):
            try:
                result.append(
                    JavItem(
                        urljoin(self.url, blk.find("a").get("href"))
                    )
                )
            except Exception as ex:
                log.debug("Error while processing div in Jav Index Page", exc_info=ex)
        return result
