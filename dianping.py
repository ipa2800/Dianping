# -*- coding:utf-8 -*-

"""
Updated at 10:40 at April 25,2019
@title: 花式反爬之大众点评
@author: Northxw
"""
# 引入所需要的包文件
import requests

import urllib.error
import numpy as np
# 引入爬虫选择器 Selector
from scrapy.selector import Selector
# 从Proxy模块中引入xdaili的API接口
from proxy import xdaili_proxy, general_proxy
# 读取配置文件
from config import HEADERS, CSS_URL, SVG_NUM_URL, \
                     SVG_FONT_URL, MONGO_CLIENT,INIT_URL
from parse import parse
from pymongo import MongoClient
# tqdm是一个进度条模块
from tqdm import tqdm
import time
import random


class Dianping(object):
    def __init__(self):
        self.headers = HEADERS
        self.proxies = xdaili_proxy()
        self.css_url = CSS_URL
        self.svg_num_url = SVG_NUM_URL
        self.svg_font_url = SVG_FONT_URL
        self.client = MongoClient(MONGO_CLIENT)
        self.db = self.client.dianping
        self.collection = self.db.shop

    # 读取店铺列表页面功能函数
    def get_store_list_page(self, url):
        try:
            # print(self.proxies)
            # get 函数可以很方便的调用proxy
            response = requests.get(url, headers=self.headers, proxies=self.proxies)
            # 不使用代理的方式
            #response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
        except urllib.error.HTTPError as e:
            print(e.reason)
    # 
    def parse_data(self, response):
        res = Selector(text=response.text)
        try:
            li_list = res.xpath('//*[contains(@class, "shop-all-list")]/ul/li')
            if li_list:
                for li in li_list:
                    data = parse(li, self.svg_num_url, self.svg_font_url, self.css_url)
                    # print(data)
                    self.save_to_db(data)
                    # break
        except Exception as e:
            print('Error: %s, Please Check it.' % e.args)

    def save_to_db(self, data):
        self.collection.insert_one(data)

    def main(self):
        """
        主函数
        """
        for i in range(10):
        # for i in tqdm(range(10), desc='Grabbing', ncols=100):
            print("第%d页：" %(i+1))
            CURRENT_URL=INIT_URL.format(str(i+1))
            print(CURRENT_URL)
            response = self.get_store_list_page(CURRENT_URL)
            #response.text 返回相应的http内容
            #print(response.text)
            self.parse_data(response)
            time.sleep(np.random.randint(1,3))
            # 测试仅抓取第一页
            # break

if __name__ == '__main__':
    dianping = Dianping()
    dianping.main()