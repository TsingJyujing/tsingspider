import json
import logging
import unittest

from tsing_spider.porn import xhamster, sex8cc, caoliu
from tsing_spider.porn.xvideos import XVideoIndexPage, XVideosVideoPage
from tsing_spider.util import http_get_soup

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)


class XhamsterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.pages = []
        for i in (1, 2):
            ip = xhamster.XhamsterIndex(i)
            cls.pages += ip.videos
            log.info("PageCount({})={}".format(i, ip.page_count))
        cls.test_obj = cls.pages[-1]

    def test_video_info(self):
        log.info(self.test_obj.json)


class XvideosTest(unittest.TestCase):

    def test_index_page(self):
        log.info(XVideoIndexPage(0).video_id_list)
        log.info(XVideoIndexPage(10).video_id_list)

    def test_video_page(self):
        page = XVideosVideoPage(video_id=XVideoIndexPage(0).video_id_list[0])
        log.info("PageInfo:\n" + json.dumps({
            "title": page.title,
            "video_link": page.video_link,
            "preview_images": page.preview_images,
            "categories": page.categories,
            "id": page.video_id,
            "uri": page.relative_uri,
            "url": page.url,
            "size": page.size,
            "duration": page.duration
        }, indent=2))


class CaoliuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        urls = caoliu.CaoliuIndexPage(2).thread_urls
        cls.thread: caoliu.CaoliuThread = caoliu.CaoliuThread(urls[0])
        assert cls.thread.soup is not None, "Data download failed."
        log.info("setUpClass successfully")

    def test_get_title(self):
        log.info(
            self.thread.json
        )


class Sex8ccTest(unittest.TestCase):

    def test_forum_group(self):
        g = sex8cc.ForumGroup(739)
        log.info(g.forums_ids)

    def test_forum(self):
        f = sex8cc.Forum(110)
        log.info(f.get_page_count())

    def test_forum_page_thread(self):
        f = sex8cc.ForumPage(157, 1)
        urls = f.thread_list_url
        log.info("Get {} urls: \n{}".format(
            len(urls),
            "\n".join(urls)
        ))
        th = sex8cc.ForumThread(urls[0])
        log.info("PageInfo:\n" + json.dumps(th.json, indent=2))


if __name__ == '__main__':
    unittest.main()
