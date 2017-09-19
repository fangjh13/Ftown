#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from config import headers, user_agent
import requests
import random
import re
import os
import pymysql

# import local environment
if os.path.exists('../../.env'):
    with open('../../.env') as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value

class GetPage(object):
    def __init__(self, url):
        self.url = url
        self.headers = headers
        self.headers['user-agent'] = random.choice(user_agent)

    def get(self):
        return requests.get(self.url, headers=self.headers).text


def top_five_books():
    ''' 抓取豆瓣图书虚构类2本非虚构类3本 '''
    rs = []
    # 虚构类
    f = GetPage("https://book.douban.com/chart?subcat=F")
    # 非虚构类
    i = GetPage("https://book.douban.com/chart?subcat=I")
    html_f = f.get()
    html_i = i.get()
    reg = r'<a\sclass=\"fleft\"\shref=\"(.*)\">(.+)</a>'
    cnt_f = re.findall(reg, html_f)[:2]
    rs.extend(cnt_f)
    cnt_i = re.findall(reg, html_i)[:3]
    rs.extend(cnt_i)
    return rs

def store(table_name, *args):
    # 根据表名分别储存到数据库
    conn = pymysql.connect(host='localhost',
                           user=os.getenv('FTOWNUSER'),
                           password=os.getenv('FTOWNPASSWD'),
                           db='collection',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO `{}` (`url`, `title`) VALUES (%s, %s)".format(table_name)
            cursor.execute(sql, *args)
        conn.commit()
    finally:
        conn.close()


if __name__ == '__main__':
    books = top_five_books()
    # 写入表名为books数据库
    for e in books:
        store('books', e)
