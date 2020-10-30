from typing import List
from urllib.parse import urlparse

from tsing_spider.util import LazySoup


class XarthunterItemPage(LazySoup):
    def __init__(self, url: str):
        super().__init__(url)

    @property
    def title(self) -> str:
        return self.soup.find("h1", attrs={"class": "header-inline"}).get_text()

    @property
    def author(self) -> str:
        author_block = self.soup.find("div", attrs={"class": "link-btn"})
        if author_block.find("a") is not None:
            return author_block.find("a").get_text()
        elif author_block.find("div"):
            return author_block.find("div").get_text()
        else:
            raise IndexError("Can't find author in this page")

    @property
    def author_url(self) -> str:
        author_block = self.soup.find("div", attrs={"class": "link-btn"})
        if author_block.find("a") is not None:
            return author_block.find("a").get("href")
        else:
            raise IndexError("Can't find author URL in this page")

    @property
    def author_id(self) -> str:
        return [s for s in urlparse(self.author_url).path.split("/") if s != ""][-1]

    @property
    def like_count(self) -> int:
        return int(self.soup.find("span", attrs={"id": "thelike"}).get_text())

    @property
    def dislike_count(self) -> int:
        return int(self.soup.find("span", attrs={"id": "thedown"}).get_text())

    @property
    def image_urls(self) -> List[str]:
        urls = []
        for ul in self.soup.find_all("ul", attrs={"class": "list-justified2"}):
            for a in ul.find_all("a"):
                urls.append(a.get("href"))
        return urls

    @property
    def preview_image_url(self) -> str:
        return self.soup.find("video").get("poster")

    @property
    def mp4_video_url(self) -> str:
        return self.soup.find("video").find("source", attrs={"type": "video/mp4"}).get("src")

    @property
    def is_video_page(self):
        try:
            _ = self.mp4_video_url
            return True
        except:
            return False

    @property
    def is_image_page(self):
        if not self.is_video_page:
            return len(self.image_urls) > 0

    @property
    def json(self) -> dict:
        doc = dict(
            title=self.title,
            author=self.author,
            like_count=self.like_count,
            dislike_count=self.dislike_count,
        )
        if self.is_video_page:
            doc["preview_image_url"] = self.preview_image_url
            doc["mp4_video_url"] = self.mp4_video_url
        elif self.is_image_page:
            doc["image_urls"] = self.image_urls
        else:
            raise Exception("No useful content in this page")
        try:
            doc["author_url"] = self.author_url
            doc["author_id"] = self.author_id
        except:
            pass
        return doc


class BaseXarthunterIndexPage(LazySoup):
    def __init__(self, url: str):
        super().__init__(url)
        self._item_urls_lazy = None

    @property
    def _item_urls(self):
        if self._item_urls_lazy is None:
            urls = []
            for ul in self.soup.find_all("ul", attrs={"class": "gallery-a"}):
                for li in ul.find_all("li"):
                    url = li.find("a").get("href")
                    if url.startswith("https://www.xarthunter.com/"):
                        urls.append(url)
            self._item_urls_lazy = urls
        return self._item_urls_lazy


class XarthunterImageIndexPage(BaseXarthunterIndexPage):
    def __init__(self, url: str):
        super().__init__(url)

    @property
    def items(self):
        return [XarthunterItemPage(x) for x in self._item_urls]

    @staticmethod
    def create(page_index: int):
        return XarthunterImageIndexPage(f"https://www.xarthunter.com/latest-updates/page/{page_index}/")


class XarthunterVideoIndexPage(BaseXarthunterIndexPage):
    def __init__(self, url: str):
        super().__init__(url)

    @property
    def items(self):
        return [XarthunterItemPage(x) for x in self._item_urls]

    @staticmethod
    def create(page_index: int):
        return XarthunterImageIndexPage(f"https://www.xarthunter.com/videos/page/{page_index}/")
