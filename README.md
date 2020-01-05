# DataSpider

[![CircleCI](https://circleci.com/gh/TsingJyujing/DataSpider.svg?style=svg)](https://circleci.com/gh/TsingJyujing/DataSpider)

让大家方便的使用各种数据

## Install

```bash
pip3 install -e git+https://github.com/TsingJyujing/DataSpider.git#egg=TsingSpider
```

## 前言
数据获取最脏最累的活就是下载和清洗数据，其中下载各种各样的数据其实是很要命的事情。
这个爬虫系统所做的事情就是将肮脏的部分包裹起来，能通过代码获取干净的数据（至于怎么存储就不是在下关心的问题了）

说是爬虫系统，其实并不是传统意义上的爬虫，而是更加倾向于搜索和收集信息的一个接口。

希望大家能玩得开心。

**有一些爬虫因为不可描述的原因我不会放文档，见谅。**

## 财经爬虫
### 财新网爬虫
财新网爬虫与其说是爬虫，不如说是一个<搜索-下载>系统。
首先要获取所有的文章链接，请使用这个接口：
```python
from tsing_spider.finance.caixin_news import query_urls
query_urls(from_date, to_date, query_words)
```
该函数的作用是搜索所有的含有query_words的文章超链接，其中：
from_date和to_date是开始和结束时间，query_words是关键词。
时间格式：yyyy-mm-dd
使用样例：
```python
query_urls('2016-09-01', '2016-09-30', '英镑')
```

## 社交网络爬虫
### 豆瓣爬虫（已经失效）
豆瓣爬虫使用了豆瓣的API，但是貌似获取的频次有限制，如果有豆瓣的API Key的希望能贡献一下。
目前仅仅支持书籍和电影。
API格式如下(以获取书籍的JSON结构体为例)：
```python
from tsing_spider.social_network import get_book_json
get_book_json(ID)
```
请直接查看文件的注释，函数命名的格式是：

`get_[movie/book]_[json/info](id)`

## 其它爬虫
### DNC邮件泄露事件
这个文件可以下载2016年美国民主党邮件服务器泄露事件所泄露出的所有邮件，大约有两万多封，但是由于服务器比较特殊，需要翻墙才能下载。
其中包含`get_mail_data`和`save_mail`两个接口，一个仅仅读取为字符串，另一个仅仅保存到本地。
