import json
import unittest

from tsing_spider.bdata.porn import xhamster, caoliu, sex8cc
from tsing_spider.bdata.porn.xvideos import XVideoIndexPage, XVideosVideoPage
from tsing_spider.blib.pyurllib import http_get_soup, http_get


class XhamsterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = http_get_soup(
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
        with self.assertRaises(NotImplementedError):
            xhamster.get_preview_images(self.data)

    def test_get_rating(self):
        print(xhamster.get_rating(self.data))

    def test_get_title(self):
        print(xhamster.get_title(self.data))


class XvideosTest(unittest.TestCase):

    def test_index_page(self):
        index_page = XVideoIndexPage(10)
        print(index_page.video_id_list)

    def test_video_page(self):
        page = XVideosVideoPage(video_id=50043631)
        print("PageInfo:\n" + json.dumps({
            "title": page.title,
            "video_link": page.video_link,
            "preview_images": page.preview_images,
            "categories": page.categories,
            "id": page.video_id,
            "uri": page.relative_uri,
            "url": page.url
        }, indent=2))


class CaoliuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        urls = caoliu.get_latest_urls(2)
        cls.data = http_get_soup(urls[0])
        assert cls.data is not None, "Data download failed."
        print("setUpClass successfully")

    def test_get_title(self):
        print(caoliu.get_page_title(self.data))

    def test_get_text(self):
        print(caoliu.get_page_text(self.data))

    def test_get_images(self):
        print(caoliu.get_page_images(self.data))


class Sex8ccTest(unittest.TestCase):

    def test_forum_group(self):
        g = sex8cc.ForumGroup(739)
        print(g.forums_ids)

    def test_forum(self):
        f = sex8cc.Forum(110)
        print(f.get_page_count())

    def test_forum_page_thread(self):
        f = sex8cc.ForumPage(157, 1)
        print(f.thread_list_url)
        th = sex8cc.ForumThread(f.thread_list_url[0])
        print("PageInfo:\n" + json.dumps(th.create_document(), indent=2))
        for i, url in enumerate(th.image_list):
            http_get(url)


if __name__ == '__main__':
    unittest.main()
