#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-5
@author: Yuan Yi fan
"""

import psycopg2
import string
import threading
import traceback


def genSQLConnection():
    return psycopg2.connect(
        database="pvideo",
        user="postgres",
        password="979323",
        host="192.168.1.103",
        port="5432")


def getRatedVideos(conn):
    sql_cmd = """
SELECT id, title, img_urls, categories, rating, video_time, download_link, myrate
FROM public.xhamster_spider WHERE myrate is not null """
    cur = conn.cursor()
    cur.execute(sql_cmd)
    res = cur.fetchall()
    cur.close()
    return res


def getCategoriesSet(res):
    tag_set = set([])
    for row in res:
        tag_set |= set(row[3])
    return tag_set


def main():
    conn = genSQLConnection()
    result_set = getRatedVideos(conn)
    tags = getCategoriesSet(result_set)
    print tags
    print "get %d tags:" % len(tags)

if __name__ == "__main__":
    main()