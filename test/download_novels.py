#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-3
@author: Yuan Yi fan
"""

from bdata.porn.yiren22 import *
from blib.str_util import *
import psycopg2
import sys
import multiprocessing
import time

reload(sys)
sys.setdefaultencoding('utf8')
retry_times = 5


def init_sql_conn():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="979323846",
        host="localhost",
        port="5432")


def exe_sql(sql_connection, sql_cmd):
    cur = sql_connection.cursor()
    try:
        cur.execute(sql_cmd)
    finally:
        sql_connection.commit()
        cur.close()


def url_in_sql(sql_connection, url_detect):
    cur = sql_connection.cursor()
    url_exist = 0
    try:
        sql_cmd = "select count(*) from \"PornNovels\" where url='%s'" % url_detect
        cur.execute(sql_cmd)
        url_exist = cur.fetchall()[0][0] > 0
    finally:
        sql_connection.commit()
        cur.close()
    return url_exist

def processing_block(block_url):
    conn = init_sql_conn()
    continue_flag_block = 0
    for retry_index_block in range(retry_times):
        try:
            list_page_count = get_novel_list_count(block_url)
            break
        except:
            if retry_index_block == (retry_times - 1):
                continue_flag_block = 1
    if continue_flag_block > 0:
        print "Jmp a except in block"
        return

    print "Get %d novel lists" % list_page_count
    for i in range(list_page_count):
        continue_flag = 0
        for retry_index in range(retry_times):
            try:
                url_list = get_novel_list(block_url, i)
                break
            except:
                if retry_index == (retry_times - 1):
                    continue_flag = 1
        if continue_flag > 0:
            print "Jmp a except in list page"
            continue
        print "Get %d novel urls(%d/%d) in %s" % (len(url_list), i + 1, list_page_count, block_url)
        for url in url_list:
            if url_in_sql(conn, url):
                continue
            for i in range(retry_times):
                try:
                    novel_title_got, novel_text_got = get_novel(url)
                    sql_upd = "INSERT INTO \"PornNovels\" (url, title, novel_text) VALUES ('%s', '%s', '%s')"
                    # print "Get novel: ", novel_title_got
                    print "Get novel: ", url
                    print "Novel basic info:(%d words)" % (len(novel_text_got))
                    # Write 2 database
                    novel_title_got = SQL_replace(novel_title_got)
                    novel_text_got = SQL_replace(novel_text_got)
                    exe_sql(conn, sql_upd % (url, novel_title_got, novel_text_got))
                    break
                except:
                    if i == (retry_times - 1):
                        print "Failed: ", url

if __name__ == "__main__":
    # Generate SQL Connection

    # NovelTest
    blocks = get_novel_blocks()
    record = []
    for block_url_iv in blocks:
        process = multiprocessing.Process(target=processing_block, args=(block_url_iv,))
        process.start()
        time.sleep(0.5)
        record.append(process)
    print "All process started."

    for process in record:
        process.join()