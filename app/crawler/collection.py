#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from config import headers, user_agent
import requests
import random
import re
import os
import pymysql
from bs4 import BeautifulSoup

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
    reg = r'class=\"subject-cover\".*?src=\"(.+?)\".*?<a\sclass=\"fleft\"\shref=\"(.*?)\">(.+?)</a>.*?color\-gray\">(.*?)</p>'
    def filter_author(a):
        rs = []
        for index, i in enumerate(a):
            if index == 3:
                i = i.strip().split('/')[0].strip()
            rs.append(i)
        return rs
    cnt_f = re.findall(reg, html_f, re.S)[:2]
    rs.extend(list(map(filter_author, cnt_f)))
    cnt_i = re.findall(reg, html_i, re.S)[:3]
    rs.extend(list(map(filter_author, cnt_i)))
    return rs


def github_trending():
    ''' 爬取github trending '''
    rs = []
    html = GetPage('https://github.com/trending').get()
    soup = BeautifulSoup(html, 'lxml')
    items= soup.find_all('li', class_='col-12')
    for i in items:
        x = []
        x.append(i.find('a').contents[2].strip())
        x.append('https://github.com' + i.find('a')['href'])
        try:
            x.append(i.find('p').string.strip())
        except AttributeError:
            x.append('')
        try:
            x.append(i.find('span',
                    attrs={'itemprop': 'programmingLanguage'}).string.strip())
        except AttributeError:
            x.append('')
        x.append(i.find('a', class_='mr-3').contents[2].strip())
        rs.append(x)
    return rs


def truncate(table_name):
    '''清空表'''
    conn = pymysql.connect(host='localhost',
                           user=os.getenv('FTOWNUSER'),
                           password=os.getenv('FTOWNPASSWD'),
                           db='collection',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            # 清空表
            sql = "TRUNCATE TABLE `{}`".format(table_name)
            cursor.execute(sql)
        conn.commit()
    finally:
        conn.close()


def store(table_name, columns, *args):
    '''根据表名分别储存到数据库'''
    conn = pymysql.connect(host='localhost',
                           user=os.getenv('FTOWNUSER'),
                           password=os.getenv('FTOWNPASSWD'),
                           db='collection',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            n = len(columns.split(','))
            sql = "INSERT INTO `{}` ({}) VALUES ({})".format(table_name, columns, ','.join(['%s'] * n))
            cursor.execute(sql, *args)
        conn.commit()
    finally:
        conn.close()


if __name__ == '__main__':
    # 豆瓣图书
    truncate('books')
    books = top_five_books()
    # 写入表名为books数据库
    for e in books:
        store('books', '`image`,`url`, `title`, `author`',e)

    # github trending
    truncate('trends')
    projects = github_trending()
    for p in projects:
        store('trends', '`project`, `url`, `desc`, `language`, `star`', p)
