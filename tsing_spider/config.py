#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan

配置文件，记录各种配置
"""
import re
import sqlite3
from http.cookiejar import CookieJar, Cookie
from typing import Optional
from warnings import warn

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# 响应超时
__REQUEST_TIMEOUT = 25


def get_request_timeout():
    return __REQUEST_TIMEOUT


def set_request_timeout(value: float):
    global __REQUEST_TIMEOUT
    __REQUEST_TIMEOUT = value


# 浏览器的User Agent参数
__USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"


def get_request_header(url: str = None, additional_header: dict = None):
    headers = {
        'User-Agent': get_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    }
    if url is not None:
        headers['Host'] = re.findall('://.*?/', url, re.DOTALL)[0][3:-1]
    if additional_header is not None:
        for k, v in additional_header.items():
            headers[str(k)] = str(v)
    return headers


def get_user_agent():
    return __USER_AGENT


def set_user_agent(value: str):
    global __USER_AGENT
    __USER_AGENT = value


# XML解析器

__XML_DECODER = 'lxml'


def get_xml_decoder():
    return __XML_DECODER


def set_xml_decoder(value: str):
    global __XML_DECODER
    __XML_DECODER = value


# 草榴网站域名

__CAOLIU_HOST = "t66y.com"


def get_caoliu_host():
    return __CAOLIU_HOST


def set_caoliu_host(value: str):
    global __CAOLIU_HOST
    __CAOLIU_HOST = value


# Cookies相关设置

__COOKIES_PATH = None
requests_session = requests.Session()

requests_session.mount(
    "http",
    HTTPAdapter(
        max_retries=Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )
    )
)


def set_request_session(new_session: requests.Session):
    global requests_session
    requests_session = new_session


def reset_request_session():
    set_request_session(requests.Session())


def get_request_session() -> requests.Session:
    return requests_session


def set_proxies(proxy_info: dict):
    """
    Set proxies for session
    :param proxy_info: {
                            'http': 'socks5://user:pass@host:port',
                            'https': 'socks5://user:pass@host:port'
                        }
    :return:
    """
    get_request_session().proxies = proxy_info


def _init_cookies(cookie_jar: CookieJar, firefox_cookies_path: str):
    """
    Initialize cookies from firefox
    :param cookie_jar:
    :param firefox_cookies_path:
    :return:
    """
    if firefox_cookies_path is None:
        firefox_cookies_path = __COOKIES_PATH
    con = sqlite3.connect(firefox_cookies_path)
    cur = con.cursor()
    # noinspection SqlResolve
    cur.execute("SELECT host, path, isSecure, expiry, name, value FROM moz_cookies")
    for item in cur.fetchall():
        c = Cookie(
            0,
            item[4],
            item[5],
            None,
            False,
            item[0],
            item[0].startswith('.'),
            item[0].startswith('.'),
            item[1],
            False,
            item[2],
            item[3],
            item[3] == "",
            None, None, {}
        )
        cookie_jar.set_cookie(c)
    return cookie_jar


def set_cookies(firefox_cookies_path: Optional[str]):
    """
    显式设置Cookies
    :param firefox_cookies_path:
    :return:
    """
    global __COOKIES_PATH
    __COOKIES_PATH = firefox_cookies_path
    if firefox_cookies_path is None:
        warn("Haven't set a valid cookies path, use default.")
        get_request_session().cookies = CookieJar()
    else:
        try:
            get_request_session().cookies = _init_cookies(CookieJar(), firefox_cookies_path)
        except:
            warn("Error while loading firefox cookies from: {}, please check it.".format(__COOKIES_PATH))


# If we have default cookies path, set here
set_cookies(None)
