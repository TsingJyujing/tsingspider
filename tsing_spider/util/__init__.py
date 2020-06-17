# -*- coding: utf-8 -*-
"""
模块说明：
    这个模块用来放置一些公共的，基础的库，也就是大部分代码都要使用的库
"""

from .pyurllib import http_get, http_get_soup, LazyContent, LazySoup, \
    DownloadTask, LiteDataDownloader, LiteFileDownloader

from .tools import process_html_string, priority_get_from_dict, try_to_json

from .hls import M3U8Downloader
