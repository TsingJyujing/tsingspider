import json
import logging
import unittest

import pytest

from tsing_spider.porn import xhamster, sex8cc, caoliu
from tsing_spider.porn.everia_club import EveriaIndex, EveriaPage
from tsing_spider.porn.jav import JavItem, BaseJavIndex
from tsing_spider.porn.xarthunter import (
    XarthunterImageIndexPage,
    XarthunterItemPage,
    XarthunterVideoIndexPage,
)
from tsing_spider.porn.xvideos import XVideoIndexPage, XVideosVideoPage
from tsing_spider.util import M3U8Downloader

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)


class EveriaTest(unittest.TestCase):
    def test_index(self):
        log.info(EveriaIndex.create(2).pages)

    def test_page(self):
        log.info(EveriaPage(
            'https://everia.club/2020/11/08/ai-takanashi-'
            '%e9%ab%98%e6%a2%a8%e3%81%82%e3%81%84-minisuka-'
            'tv-2020-10-29-limited-gallery-3-1/'
        ).json)


class XarthunterTest(unittest.TestCase):
    def test_image_index_page(self):
        for url in XarthunterImageIndexPage.create(2)._item_urls:
            log.info(url)

    def test_video_index_page(self):
        for url in XarthunterVideoIndexPage.create(2)._item_urls:
            log.info(url)

    def test_image_item_page(self):
        log.info(
            XarthunterItemPage(
                "https://www.xarthunter.com/top-class-blonde-model-gets-pleased-with-nice-sex-by-her-man-17732/").json
        )

    def test_video_item_page(self):
        log.info(
            XarthunterItemPage("https://www.xarthunter.com/keira-perfect-timing-video/").json
        )


class JavTest(unittest.TestCase):
    def test_index_page(self):
        bi = BaseJavIndex("h.javtorrent.re", category="h-manga", page=1)
        log.info([
            item.url
            for item in bi.items
        ])

    def test_item(self):
        test_item = JavItem("http://javtorrent.re/uncensored/202571/")
        log.info(test_item.json)
        for torrent in test_item.torrents:
            log.info(f"Torrent Size: {len(torrent)}")
        for magnet_uri in test_item.magnet_uris:
            log.info(f"Magnet URI: {magnet_uri}")
        log.info(f"Image Size: {len(test_item.image)}")


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

    def test_search(self):
        log.info(xhamster.XhamsterSearch("asian creampie").video_urls)


@pytest.mark.skip(reason="This unit test failed in CircleCI, but works in my local, maybe network problem")
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
        log.info("setUpClass successfully with url={}".format(urls[0]))

    def test_get_title(self):
        log.info(
            self.thread.json
        )


class Sex8ccTest(unittest.TestCase):

    def test_forum_group(self):
        g = sex8cc.ForumGroup(739)
        log.info(g.forums_ids)

    def test_forum(self):
        f = sex8cc.Forum(11)
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

    def test_download_video(self):
        ft = sex8cc.ForumThread("https://sex8.cc/thread-14413541-1-1.html")
        url = ft.m3u8_video_links[0]
        log.info(f"Downloading {url}")
        M3U8Downloader(url).download_to("test.ts")


if __name__ == '__main__':
    unittest.main()
