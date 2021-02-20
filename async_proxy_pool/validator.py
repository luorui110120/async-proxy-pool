#!/usr/bin/env python
# coding=utf-8

import os,datetime,time
import asyncio

from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp

from urllib import error
from urllib.request import ProxyHandler, build_opener

from .config import VALIDATOR_BASE_URL, VALIDATOR_BATCH_COUNT, REQUEST_TIMEOUT, TEST_SPEED_COUNT
from .logger import logger
#from .database import RedisClient
from .data_sqlite3 import SQLite3Client


VALIDATOR_BASE_URL = os.environ.get("VALIDATOR_BASE_URL") or VALIDATOR_BASE_URL


class Validator:
    def __init__(self):
        self.sqlite3 = SQLite3Client()

    async def test_proxy(self, proxy):
        """
        测试代理

        :param proxy: 指定代理
        """
        async with aiohttp.ClientSession() as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode("utf8")
                async with session.get(
                    VALIDATOR_BASE_URL, proxy=proxy, timeout=REQUEST_TIMEOUT
                ) as resp:
                    if resp.status == 200:
                        self.sqlite3.increase_proxy_score(proxy)

                        logger.info("Validator √ {}".format(proxy))
                    else:
                        self.sqlite3.reduce_proxy_score(proxy)
                        logger.info("Validator × {}".format(proxy))
            except:
                self.sqlite3.reduce_proxy_score(proxy)
                logger.info("Validator × {}".format(proxy))
    def test_proxy_new(self, proxy):
            try:
                starttime = datetime.datetime.now()
                typestr = 'https' if proxy.find('https') >= 0 else 'http'
                proxy_handler = ProxyHandler({typestr: proxy})
                opener = build_opener(proxy_handler)
                ##// 延迟3秒
                url = "%s://%s" % (typestr, VALIDATOR_BASE_URL)
                reqs = opener.open(url, timeout=3)
                logger.info("ip: {}".format(reqs.read()))
                endtime = datetime.datetime.now()
                speed = (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds
                self.sqlite3.update_proxy_speed(proxy, speed / 1000000)
                if reqs.status == 200:
                    self.sqlite3.increase_proxy_score(proxy)
                    logger.info("Validator √ {}| speed {}".format(proxy, speed / 1000000))
                else:
                    self.sqlite3.reduce_proxy_score(proxy)
                    logger.info("Validator × {}".format(proxy))
            except:
                self.sqlite3.reduce_proxy_score(proxy)
                logger.info("Validator × {}".format(proxy))
    def openUrl(self, proxyAddr):
        totalS = 0
        # 测试，取10次平均值
        for i in range(TEST_SPEED_COUNT):
            try:
                starttime = datetime.datetime.now()
                # 使用无验证的代理
                # proxy_handler = urllib.ProxyHandler({"http": proxyAddr})
                typestr = 'https' if proxyAddr.find('https') >= 0 else 'http'
                proxy_handler = ProxyHandler({typestr: proxyAddr})
                opener = build_opener(proxy_handler)
                ##// 延迟3秒
                opener.open(VALIDATOR_BASE_URL, timeout=3)
                endtime = datetime.datetime.now()
                logger.info(str(endtime - starttime) + "|" + proxyAddr)
                totalS += (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds
            except error.URLError as e:
                # 输出错误信息，如果代理一直出错，该代理应该废弃
                logger.info(proxyAddr + "|" + str(e))
                totalS += 10 * 1000000
                if (str(e) == "<urlopen error (10054, 'Connection reset by peer')>"
                        or str(e) == "<urlopen error (10060, 'Operation timed out')>"
                        or str(e) == "<urlopen error (10061, 'Connection refused')>"
                        or str(e) == "<urlopen error (10065, 'No route to host')>"
                        or str(e) == "HTTP Error 502: Bad Gateway"
                        or str(e) == "HTTP Error 503: Service Unavailable"
                        or str(e) == "HTTP Error 504: Gateway Time-out"
                        or str(e) == "HTTP Error 404: Not Found"
                ):
                # openUrl(proxyAddr)
                # return
                    totalS += 10 * 1000000
            except Exception as e:
                logger.info(proxyAddr + "|" + "httplib.BadStatusLine")
                # 出错就重试
                # openUrl(proxyAddr)
                # return
                totalS += 10 * 1000000
        logger.info(totalS)
        # 输出10次的平均值，单位秒
        return totalS / TEST_SPEED_COUNT / 1000000
    def run(self):
        """
        启动校验器
        """
        logger.info("Validator working...")
        logger.info("Validator website is {}".format(VALIDATOR_BASE_URL))
        proxies = self.sqlite3.all_proxies()
        #### http 的校验
        # loop = asyncio.get_event_loop()
        # for i in range(0, len(proxies), VALIDATOR_BATCH_COUNT):
        #     _proxies = proxies[i : i + VALIDATOR_BATCH_COUNT]
        #     tasks = [self.test_proxy(proxy) for proxy in _proxies]
        #     if tasks:
        #         loop.run_until_complete(asyncio.wait(tasks))
        #print("https Count:%d" % len(proxies))
        ###### 自定义的校验函数,速度不快
        for proxy in proxies:
            self.test_proxy_new(proxy)

        ###测网速
        # proxies = self.sqlite3.get_score_proxies(10)
        # print("testSpeed Count:%d"%len(proxies))
        # for proxy in proxies:
        #     logger.info("testSpeed {}".format(proxy))
        #     speed = self.openUrl(proxy )
        #     self.sqlite3.update_proxy_speed(proxy, speed)

        ##### //多线程并发测试 容易崩溃,目前还没找到原因
        # with ThreadPoolExecutor(max_workers=10) as t:
        #     obj_list = []
        #     for page in proxies:
        #         obj = t.submit(self.test_proxy_new, page)
        #         obj_list.append(obj)
        #
        #     for future in as_completed(obj_list):
        #         pass
        logger.info("Validator resting...")


validator = Validator()
