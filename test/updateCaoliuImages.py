# !/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import psycopg2
import sys
import os

sys.path.append("..")
from blib.pyurllib import LiteFileDownloader
from blib.str_util import *
from bdata.porn.caoliu import *


def genSQLConnection():
    return psycopg2.connect(
        database="pvideo",
        user="postgres",
        password="979323",
        host="192.168.1.103",
        port="5432")


save_path = "/media/yuanyifan/ext_data/img_pool/"


def get_current_index(sql_connection):
    cur = sql_connection.cursor()
    sql_cmd = "select max(index)+1 from public.img_list"
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    cur.close()
    return rows[0][0]


def is_url_existed(sql_connection, url):
    cur = sql_connection.cursor()
    sql_cmd = "select count(*) from public.img_list where url='%s'" % url
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    cur.close()
    return rows[0][0] > 0


def insert_pageinfo_to_db(sql_connection, index, title, url, comment_text, image_count, image_urls):
    cur = sql_connection.cursor()
    sql_cmd = "INSERT INTO public.img_list " \
              "(index, title, block, imgcount, comment, url, image_urls) " \
              "VALUES (%d,'%s', '%s', %d, '%s','%s', '%s')" % (
                  index, title, "Daguerre".upper(),
                  image_count, comment_text, url,
                  str_iterator_to_pgsql_array(image_urls))
    cur.execute(sql_cmd)
    sql_connection.commit()
    cur.close()
    return index


def execute_tasks(tasks):
    """

    :param tasks:
    :return:
    """
    for task in tasks:
        task.start()
    for task in tasks:
        task.join()


def main():
    main_conn = genSQLConnection()
    for listIndex in range(141):
        print "PROCESSING PAGE:%d" % listIndex
        urls = get_latest_urls(listIndex)
        for url in urls:
            try:
                print "Downloading: %s" % url
                if is_url_existed(main_conn, url):
                    raise Exception("URL is existed in Table!")
                page_soup = get_soup(url)
                title = get_page_title(page_soup)
                images = get_page_images(page_soup)
                text = get_page_text(page_soup)
                # Insert main_conn
                page_index = get_current_index(main_conn)
                page_path = "%s%08d/" % (save_path, page_index)
                try:
                    os.makedirs(page_path)
                except:
                    print "dir may existed."
                # create tasks
                img_task_list = [
                    LiteFileDownloader(image_url=img, filename="%s%d%s" % (page_path, i, get_extesion(img)))
                    for i, img in enumerate(images)]
                execute_tasks(img_task_list)
                # 下载以后再写入数据库
                insert_pageinfo_to_db(main_conn, page_index, title, url, text, len(images), images)
                print "Downloaded: %s" % url
            except Exception, e:
                print "Error while downloading: %s" % url
                print e.message


if __name__ == "__main__":
    main()
