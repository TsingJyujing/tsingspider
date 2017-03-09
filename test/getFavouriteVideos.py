# !/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import sys

sys.path.append("..")
from bdata.porn import xhamster
import psycopg2


def genSQLConnection():
    return psycopg2.connect(
        database="pvideo",
        user="postgres",
        password="979323",
        host="192.168.1.103",
        port="5432")


def getLikeIDSet(sql_connection, minrate):
    cur = sql_connection.cursor()
    sql_cmd = "select id from xhamster_spider where myrate>%f" % minrate
    cur.execute(sql_cmd)
    res = cur.fetchall()
    cur.close()
    return [x[0] for x in res]


if __name__ == "__main__":
    main_conn = genSQLConnection()
    LikeIDSet = getLikeIDSet(main_conn, .5)
    for page_id in LikeIDSet:
        _, sp = xhamster.getSoup(xhamster.genURL(page_id))
        print xhamster.getDownloadLink(sp)
