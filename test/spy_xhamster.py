#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import sys
sys.path.append("..")
from bdata.porn import xhamster
import psycopg2
from blib.list_file_io import read_strlist, write_strlist
import string
import threading
import traceback
import time
import Queue

saving_path = "/home/yuanyifan/Data/xhamster/xhamster_pool"
download_images = True
mutex = threading.Lock()

def genSQLConnection():
    return psycopg2.connect(
        database="pvideo",
        user="postgres",
        password="979323",
        host="localhost",
        port="5432")


def getIDSet(sql_connection):
    cur = sql_connection.cursor()
    sql_cmd = "select id from xhamster_spider"
    cur.execute(sql_cmd)
    res = cur.fetchall()
    cur.close()
    return set([x[0] for x in res])


def loadUnprocessedID():
    try:
        strlist = read_strlist("xhamster.unprocessed.list")
        return set([string.atoi(s) for s in strlist])
    except:
        return set([3369855])


def genSQLStringArray(listInput):
    listInput = ['"' + processSQLString(x) + '"' for x in listInput]
    return "{" + ",".join(listInput) + "}"


def genSQLStatment(url, sp):
    id = xhamster.getPageID(url)
    title = processSQLString(xhamster.getTitleFromSoup(sp))
    imgList = xhamster.getPreviewImgList(sp)
    imgurls = genSQLStringArray(imgList)
    if download_images:
        xhamster.downloadImgList(id, imgList, saving_path)
    categories = genSQLStringArray(xhamster.getCategories(sp))
    rating = xhamster.getRating(sp)
    video_time = xhamster.getTime(sp)
    download_link = xhamster.getDownloadLink(sp)
    return """
INSERT INTO public.xhamster_spider(
            id, title, img_urls, categories, rating, video_time, download_link)
    VALUES (%d, '%s', '%s', '%s', %d, %d, '%s');
    """ % (id, title, imgurls, categories, rating, video_time, download_link)


def exe_sql(sql_connection, sql_cmd):
    cur = sql_connection.cursor()
    try:
        cur.execute(sql_cmd)
    finally:
        sql_connection.commit()
        cur.close()


def processSQLString(raw_str):
    return raw_str.replace("'", "`")

    
def queueSQLExecutor(sql_queue):
    conn = genSQLConnection()
    while(True):
        try:
            sql_cmd = sql_queue.get(timeout=120)
            try:
                exe_sql(conn, sql_cmd)
            except Exception,e:
                print "Error to execute SQL caused by: ", e.message
            print "Executed: %s" % sql_cmd
        except:
            conn.close()
            break;
    

def process_unprocessed_set(processed_url_set, unprocessed_url_set, sql_queue):
    saving_flag = 0
    conn = genSQLConnection()
    while len(unprocessed_url_set) > 0:
        this_id = unprocessed_url_set.pop()
        if this_id in processed_url_set:
            continue
        try:
            saving_flag += 1
            this_url = xhamster.genURL(this_id)
            page_data, sp = xhamster.getSoup(this_url)
            sql_queue.put(genSQLStatment(this_url, sp))
            processed_url_set.add(this_id)
            new_ids = xhamster.getJumpUrls(page_data)
            new_ids = set([xhamster.getPageID(x) for x in new_ids]) - unprocessed_url_set
            unprocessed_url_set |= new_ids
            print "Now unprocessed list size:", len(unprocessed_url_set)
        except Exception, e:
            unprocessed_url_set.add(this_id)
            print "Error while processing %d" % this_id
            print e.message
            print traceback.format_exc()
            time.sleep(1)
            
        if saving_flag >= 1000:
            saving_flag = 0
            write_strlist(
                "xhamster.unprocessed.list",
                [("%d" % x) for x in unprocessedIDSet])


if __name__ == "__main__":
    main_conn = genSQLConnection()
    processedIDSet = getIDSet(main_conn)
    unprocessedIDSet = loadUnprocessedID() - processedIDSet
    thread_count = 80
    threads_list = []
    SQLqueue = Queue.Queue()
    
    for i in range(thread_count):
        threads_list.append(threading.Thread(
            target=process_unprocessed_set,
            args=(processedIDSet, unprocessedIDSet, SQLqueue)))
    
    for th in threads_list:
        th.start()

    queueSQLExecutor(SQLqueue)
    
    for th in threads_list:
        th.join()
