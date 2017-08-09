# !/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import sys
sys.path.append("..")

import os
import time
import shutil
import string
import datetime

import psycopg2
import threadpool
from DBUtils.PooledDB import PooledDB
from PIL import Image
import cv2

from blib.list_operation import list_unique
from blib.pyurllib import LiteDataDownloader
from blib.str_util import *
from bdata.porn.caoliu import *

conn_pool_size = 32
thread_count = 72
page_to_read = 5
files_count_limit_delete_dir = 2
save_path = "/media/yuanyifan/ext_data/img_pool/"
sleep_seconds = 23*3600 # 23Hours
model_file  = "models/haarcascade_frontalface_alt2.xml"

pool = PooledDB(psycopg2,
                conn_pool_size,
                database="pvideo",
                user="postgres",
                password="979323",
                host="192.168.1.103",
                port="5432")

face_cascade = cv2.CascadeClassifier(model_file)

def count_face(image_name, min_window=1.2, max_window=5):
    try:
        img = cv2.imread(image_name)
        return len(face_cascade.detectMultiScale(img, min_window,max_window))
    except:
        return 0
    
    
def count_face_in_dir(dir_name,  min_window=1.2, max_window=5):
    return sum([count_face(os.path.join(dir_name,filename), min_window, max_window) for filename in os.listdir(dir_name)])
    
    
def write_facecount(conn,index,face_count): 
    cur = conn.cursor()
    cur.execute("UPDATE public.img_list SET face_count=%d WHERE index=%d" % (face_count,index))
    conn.commit()
    cur.close()
    
def read_facecount(conn,index):
    cur = conn.cursor()
    sql_cmd = "select face_count from public.img_list where index=%d" % index
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    cur.close()
    return rows[0][0]

def get_all_nofacecount(conn):
    cur = conn.cursor()
    sql_cmd = "select index from public.img_list where face_count<0"
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    cur.close()
    return [row[0] for row in rows]
    
def count_faces():
    conn = get_connection()
    try:
        indeces = get_all_nofacecount(conn);
        for i in indeces:
            try:
                dir_name = os.path.join(save_path,"%08d" % i)
                face = count_face_in_dir(dir_name, 1.1, 5)
                write_facecount(conn,i,face)
                print "There're %d faces in index=%d" % (face,i)
            except:
                print "Error while counting faces in %d" % i
    except Exception,err:
        print "Error while counting faces", err.message
    finally:
        conn.close()
        
        
def is_valid_image(filename):
    try:
        img = Image.open(filename)
        img.close()
        return True
    except:
        return False
        
        
def remove_empty_dir(delete_limit):
    conn = get_connection()
    try:
        img_pool_dirs = os.listdir(save_path)
        for img_dir in img_pool_dirs:
            img_list_index = string.atoi(img_dir)
            current_dir = os.path.join(save_path,img_dir)
            files_in_dir = os.listdir(current_dir)
            for filename in files_in_dir:
                full_filename = os.path.join(current_dir,filename)
                is_valid = is_valid_image(full_filename)
                if not is_valid:
                    os.remove(full_filename)
                    print "Image: %s deleted" % full_filename
            files_in_dir = os.listdir(current_dir)
            if len(files_in_dir)<=delete_limit:
                if not is_like(conn,img_list_index):
                    shutil.rmtree(current_dir)
                    remove_index(conn,img_list_index)
                    print "%d files in %s, removed." % (len(files_in_dir),img_dir)
    except Exception,err:
        print "Error while removing empty dirs", err.message
    finally:
        conn.close()

        
def get_connection():
    return pool.connection()


def get_urls(n):
    urls = []
    for i in range(n):
        current_page_url = get_latest_urls(i + 1)
        print "Obtained %d urls in page %d" % (len(current_page_url), i + 1)
        urls += current_page_url
    return list_unique(urls)
    
    
def remove_index(conn, index):
    cur = conn.cursor()
    cur.execute("delete from public.img_list where index=%d" % index)
    conn.commit()
    cur.close()

    
def is_url_existed(conn, url):
    cur = conn.cursor()
    sql_cmd = "select count(*) from public.img_list where url='%s'" % url
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    cur.close()
    return rows[0][0] > 0
    
    
def is_like(conn, index):
    cur = conn.cursor()
    sql_cmd = "select \"like\">0 from public.img_list where index=%d" % index
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    cur.close()
    return rows[0][0]==True


def insert_pageinfo_to_db(conn, title, url, comment_text, image_count, image_urls):
    cur = conn.cursor()
    sql_cmd = "INSERT INTO public.img_list " \
              "(index, title, block, imgcount, comment, url, image_urls) " \
              "VALUES ((SELECT max(index)+1 from public.img_list)," \
              "'%s', '%s', %d, '%s','%s', '%s') " \
              "RETURNING index" % (
                  title, "Daguerre".upper(),
                  image_count, comment_text, url,
                  str_iterator_to_pgsql_array(image_urls))
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    conn.commit()
    cur.close()
    return rows[0][0]


def process_page_url(url):
    try:
        conn = get_connection()
        #print "Downloading: %s" % url
        if is_url_existed(conn, url):
            raise Exception("URL is existed in db!")
        page_soup = get_soup(url)
        title = get_page_title(page_soup)
        images = get_page_images(page_soup)
        text = get_page_text(page_soup)
        # 下载小文件
        img_task_list = [
            LiteDataDownloader(image_url=img, tag="%d%s" % (i, get_extesion(img)))
            for i, img in enumerate(images)]
        for task in img_task_list:
            task.start()
        for task in img_task_list:
            task.join()
        page_index = insert_pageinfo_to_db(conn, title, url, text, len(images), images)
        page_path = "%s%08d/" % (save_path, page_index)
        try:
            os.makedirs(page_path)
        except:
            print "dir may existed."
        for task in img_task_list:
            task.write_file(page_path + task.tag)
        # create tasks
        print "Downloaded: %s" % url
    except Exception, e:
        #print "Error while downloading: %s" % url
        #print e.message
        pass
    finally:
        conn.close()


def download_image_lists(n):
    pool = threadpool.ThreadPool(thread_count)
    for i in range(n):
        try:
            urls = get_latest_urls(i + 1)
            print "Obtained %d urls in page %d" % (len(urls), i + 1)
            requests = threadpool.makeRequests(process_page_url, urls)
            [pool.putRequest(req) for req in requests]
            print "Requests appended to thread pool"
        except Exception,e:
            print "Error while appending thread pool:",e.message
    pool.wait()

def execute_one_cycle():
    download_image_lists(page_to_read)
    remove_empty_dir(files_count_limit_delete_dir)
    count_faces()    
    
def loopInf():
    while(True):
        execute_one_cycle()
	time.sleep(sleep_seconds)

        
if __name__ == "__main__":
    execute_one_cycle()
    with open("run.log","a") as fid:
        fid.write("Updated in " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
