#!/usr/bin/env python
# coding=utf-8

import re,time

import pyquery
from urllib.request import urlopen
import urllib
from lxml.html import parse


from .utils import requests
#from .database import RedisClient
from .data_sqlite3 import SQLite3Client
from .logger import logger


sqlite3_conn = SQLite3Client()
all_funcs = []

def collect_funcs(func):
    """
    装饰器，用于收集爬虫函数
    """
    all_funcs.append(func)
    return func


class Crawler:
    @staticmethod
    def run():
        """
        启动收集器
        """
        logger.info("Crawler working...")
        for func in all_funcs:
            for proxy in func():
                sqlite3_conn.add_proxy(proxy)
                logger.info("Crawler √ {}".format(proxy))
        logger.info("Crawler resting...")


    @staticmethod
    #@collect_funcs
    def crawl_kuaidaili():
        """
        快代理：https://www.kuaidaili.com
        """
        typelist = ['inha', 'intr']
        for proxy_type in typelist:
            ###//获取5页的代理ip
            for page_index in range(1, 5):
                #### //国内代理
                url = "https://www.kuaidaili.com/free/%s/%d/" % (proxy_type, page_index)
                html = urlopen(url)
                if html:
                    doc = parse(html)
                    time.sleep(1)
                    for trval in doc.xpath('//*[@id="list"]/table/tbody/tr'):
                        ip = trval.xpath('./td[@data-title="IP"]/text()')[0]
                        port = trval.xpath('./td[@data-title="PORT"]/text()')[0]
                        schema = trval.xpath('./td[4]/text()')[0]
                        if ip and port:
                            yield "{}://{}:{}".format(schema.lower(), ip, port)

    @staticmethod
    @collect_funcs
    def crawl_proxy_list():
        """
        快代理：www.proxy-list.download
        """
        typestrs = ['HTTPS', 'HTTP']


        # for proxy_type in items:
        for typestr in typestrs:
            url = "https://www.proxy-list.download/%s" % (typestr.upper())
            headers = {'user-agent': 'mozilla/5.0'}
            url_data = urllib.request.Request(url=url, headers=headers)

            # print(r.code)

            html = urlopen(url_data)
            if html:
                # doc = pyquery.PyQuery(url=url)
                doc = parse(html)
                time.sleep(1)
                ## for tdval in doc("tbody tr").items()
                for trval in doc.xpath('//*[@id="tabli"]/tr'):
                    ip = trval.xpath('./td[1]/text()')[0]
                    port = trval.xpath('./td[2]/text()')[0]
                    if ip and port:
                        yield "{}://{}:{}".format(typestr.lower(), ip, port)
    @staticmethod
    #@collect_funcs
    def crawl_hidemy():
        """
        hidemy代理：https://hidemy.name/cn
        """
        typestrs=['http', 'https']
        for typestr in typestrs:
            url = "https://hidemy.name/cn/proxy-list/?type=%s#list" % ('s' if typestr.find('https') >= 0 else 'h')
            headers = {'user-agent': 'mozilla/5.0'}
            '''
            使用Request类添加请求头可以不使用headers这个参数。而使用这个类的实例化对象的方法
            add_header(key='user-agent',val='mozilla/5.0')
            '''
            url_data = urllib.request.Request(url=url, headers=headers)
            html = urlopen(url_data)
            if html:
                doc = parse(html)
                ### 延迟1秒,请求太快会导致返回失败
                time.sleep(1)
                for trval in doc.xpath('/html/body/div[1]/div[4]/div/div[4]/table/tbody/tr'):
                    ip = trval.xpath('./td[1]/text()')[0]
                    port = trval.xpath('./td[2]/text()')[0]
                    proxy_type = trval.xpath('./td[5]/text()')[0]
                    if ip and port:
                        yield "{}://{}:{}".format(typestr, ip, port)
    @staticmethod
    #@collect_funcs
    def crawl_ip3366():
        """
        云代理：http://www.ip3366.net
        """
        url = "http://www.ip3366.net/?stype=1&page={}"

        items = [p for p in range(1, 8)]
        for page in items:
            html = requests(url.format(page))
            if html:
                doc = pyquery.PyQuery(html)
                for proxy in doc(".table-bordered tr").items():
                    ip = proxy("td:nth-child(1)").text()
                    port = proxy("td:nth-child(2)").text()
                    schema = proxy("td:nth-child(4)").text()
                    if ip and port and schema:
                        yield "{}://{}:{}".format(schema.lower(), ip, port)



crawler = Crawler()
