#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
from bdata.porn import xhamster
import psycopg2
from blib.list_file_io import read_strlist, write_strlist
import string

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
    listInput = ['"' + x + '"' for x in listInput]
    return "{" + ",".join(listInput) + "}"


def genSQLStatment(url, sp):
    id = xhamster.getPageID(url)
    title = xhamster.getTitleFromSoup(sp)
    imgList = xhamster.getPreviewImgList(sp)
    imgurls = genSQLStringArray(imgList)
    xhamster.downloadImgList(id, imgList, "D:/HTTP_DIR/xhamster_pool")
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

if __name__ == "__main__":
    conn = genSQLConnection()
    processedIDSet = getIDSet(conn)
    unprocessedIDSet = loadUnprocessedID()

    saveing_flag = 0

    while(True):
        upSize = len(unprocessedIDSet)
        if upSize == 0:
            break
        else:
            print "Unprocessed size:%d" % upSize
        this_id = unprocessedIDSet.pop()
        if this_id in processedIDSet:
            continue
        try:
            saveing_flag += 1
            this_url = xhamster.genURL(this_id)
            page_data, sp = xhamster.getSoup(this_url)
            exe_sql(conn, genSQLStatment(this_url, sp))
            processedIDSet.add(this_id)
            new_ids = xhamster.getJumpUrls(page_data)
            new_ids = set([xhamster.getPageID(x) for x in new_ids]) - processedIDSet
            unprocessedIDSet |= new_ids
        except:
            print "Error"
        if saveing_flag >= 100:
            saveing_flag = 0
            write_strlist(
                "xhamster.unprocessed.list",
                [("%d" % x) for x in unprocessedIDSet])