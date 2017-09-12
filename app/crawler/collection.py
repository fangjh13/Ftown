#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from config import headers, user_agent
import requests
import random
import re


class GetPage(object):
    def __init__(self, url):
        self.url = url
        self.headers = headers
        self.headers['user-agent'] = random.choice(user_agent)

    def get(self):
        return requests.get(self.url, headers=self.headers).text


def top_five_books():
    ''' 抓取虚构类2本非虚构类3存入数据库 '''
    rs = []
    # 虚构类
    f = GetPage("https://book.douban.com/chart?subcat=F")
    # 非虚构类
    i = GetPage("https://book.douban.com/chart?subcat=I")
    html_f = f.get()
    html_i = i.get()
    reg = r'<a\sclass=\"fleft\"\shref=\"(.*)\">'
    cnt_f = re.findall(reg, html_f)[:2]
    rs.extend(cnt_f)
    cnt_i = re.findall(reg, html_i)[:3]
    rs.extend(cnt_i)
    return rs

print(top_five_books())