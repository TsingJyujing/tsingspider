from typing import List, Optional

from tsing_spider.util import LazySoup


class EveriaPage(LazySoup):
    def __init__(self, url: str):
        super().__init__(url)

    @property
    def image_urls(self) -> List[str]:
        return [
            img.get("data-src")
            for img in self.soup.find_all("img", attrs={"class": "lazyload"})
            if img.get("fifu-featured") is None
        ]

    @property
    def category(self) -> Optional[str]:
        s = self.soup.find("a", attrs={"rel": ["category", "tag"]})
        if s is not None:
            return s.get_text()

    @property
    def title(self) -> Optional[str]:
        s = self.soup.find("h1", attrs={"class": "entry-title"})
        if s is not None:
            return s.get_text()

    @property
    def updated_time(self) -> Optional[str]:
        ut = self.soup.find("time", attrs={"class": "updated"})
        if ut is not None:
            return ut.get("datetime")

    @property
    def published_time(self) -> Optional[str]:
        ut = self.soup.find("time", attrs={"class": "published"})
        if ut is not None:
            return ut.get("datetime")

    @property
    def json(self):
        return {
            "category": self.category,
            "image_urls": self.image_urls,
            "title": self.title,
            "updated_time": self.updated_time,
            "published_time": self.published_time,
        }

    def __repr__(self):
        return f"EveriaPage(\"{self.url}\")"


class EveriaIndex(LazySoup):
    def __init__(self, url: str):
        super().__init__(url)

    @property
    def pages(self) -> List[EveriaPage]:
        urls = []
        for article in self.soup.find_all("article"):
            urls.append(article.find("a").get("href"))
        return [EveriaPage(url) for url in urls]

    @staticmethod
    def create(page_id: int, category: str = None):
        if category is not None:
            return EveriaIndex(f"https://everia.club/category/{category}/page/{page_id}/")
        else:
            return EveriaIndex(f"https://everia.club/page/{page_id}/")

    @staticmethod
    def get_all_categories():
        return ["gravure", "aidol", "magazine", "thailand", "chinese"]
