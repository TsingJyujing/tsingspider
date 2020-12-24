# DataSpider

![Upload Python Package](https://github.com/TsingJyujing/DataSpider/workflows/Upload%20Python%20Package/badge.svg)

A spider framework with several internal spiders.

## Install

```bash
pip install --upgrade tsingspider
```

## Features

- Light-weight: do not have to start browser simulator, won't cost lots of resources
    - But not all the website can download in this way
- Lazy: won't download anything before you actually use the data
- Useful Utilities
    - Support HLS download
    - Support cookies from firefox
    - Support Proxies
    - Generate magnet link from torrent data

## Write Your Own Spider

To define a resource, you can use `LazySoup` or `LazyContent`.
`LazyContent` is for binary data, basically all kinds of the data are binary.
`LazySoup` is for the XML format resource, widely be used for downloading web-page.

For example:

```python
from tsing_spider.util import LazySoup, LazyContent

class YourOwnSpider(LazySoup):
    def __init__(self, url:str):
        LazySoup.__init__(self, url)

    @property
    def some_info(self) -> str:
        """
        Extract information from self.soup
        the data will be downloaded at the first time of using it
        """
        pass
```