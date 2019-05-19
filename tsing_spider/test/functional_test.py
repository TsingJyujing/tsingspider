import unittest

from tsing_spider.bdata.porn import xvideos, xhamster, caoliu
from tsing_spider.blib.pyurllib import get_soup


class XhamsterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = get_soup(
            "https://m.xhamster.com/videos/hot-german-milf-female-teacher-show-how-to-fuck-private-11500990")
        assert cls.data is not None, "Data download failed."
        print("setUpClass successfully")

    def test_get_categories(self):
        print(xhamster.get_categories(self.data))

    def test_get_download_link(self):
        print(xhamster.get_download_link(self.data))

    def test_get_duration(self):
        print(xhamster.get_duration(self.data))

    def test_get_preview_images(self):
        print(xhamster.get_preview_images(self.data))

    def test_get_rating(self):
        print(xhamster.get_rating(self.data))

    def test_get_title(self):
        print(xhamster.get_title(self.data))


class XvideosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = get_soup("https://www.xvideos.com/video47916065/_~_~_2")

    def test_get_title(self):
        print(xvideos.get_title(self.data))

    def test_get_categories(self):
        print(xvideos.get_categories(self.data))

    def test_get_download_link(self):
        print(xvideos.get_download_link(self.data))


class CaoliuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        urls = caoliu.get_latest_urls(2)
        cls.data = get_soup(urls[0])
        assert cls.data is not None, "Data download failed."
        print("setUpClass successfully")

    def test_get_title(self):
        print(caoliu.get_page_title(self.data))

    def test_get_text(self):
        print(caoliu.get_page_text(self.data))

    def test_get_images(self):
        print(caoliu.get_page_images(self.data))


if __name__ == '__main__':
    unittest.main()
