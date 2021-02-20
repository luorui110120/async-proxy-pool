#!/usr/bin/env python
# coding=utf-8

import datetime

from urllib import error
from urllib.request import ProxyHandler, build_opener


from logger import logger
from qqwry import QQwry

# 目标URL
targetUrl = "http://www.baidu.com"
# 取多少次访问速度的平均值
testCount = 10
proxyAddrSpeedList = []


def openUrl(proxyAddr):
    totalS = 0
    # 测试，取10次平均值
    for i in range(testCount):
        try:
            starttime = datetime.datetime.now()
            # 使用无验证的代理
            # proxy_handler = urllib.ProxyHandler({"http": proxyAddr})
            proxy_handler = ProxyHandler({'http': proxyAddr})
            opener = build_opener(proxy_handler)
            ##// 延迟3秒
            opener.open(targetUrl, timeout=3)
            endtime = datetime.datetime.now()
            logger.info(str(endtime - starttime) + "|" + proxyAddr)
            totalS += (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds
        except error.URLError as e:
            # 输出错误信息，如果代理一直出错，该代理应该废弃
            logger.info(proxyAddr + "|" + str(e))
            if (str(e) == "<urlopen error (10054, 'Connection reset by peer')>"
                    or str(e) == "<urlopen error (10060, 'Operation timed out')>"
                    or str(e) == "<urlopen error (10061, 'Connection refused')>"
                    or str(e) == "<urlopen error (10065, 'No route to host')>"
                    or str(e) == "HTTP Error 502: Bad Gateway"
                    or str(e) == "HTTP Error 503: Service Unavailable"
                    or str(e) == "HTTP Error 504: Gateway Time-out"
                    or str(e) == "HTTP Error 404: Not Found"
            ):
                # 出错就重试
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
    proxyAddrSpeedList.append(str(totalS / testCount / 1000000.) + u"秒|" + proxyAddr)

def get_country(proxy):
    q = QQwry()
    q.load_file('../qqwry.dat')
    list = proxy.split(':')
    ip = list[1].strip('/')
    country = q.lookup(ip)
    if(country):
        return country[0]
    return None
# 测试的代理地址列表，逗号分隔
proxyAddressArray = "http://95.104.54.227:42119,http://47.52.239.156:3128".split(",")
def test_main(listTest):
    for p in proxyAddressArray:
        openUrl(p)
        print("已测试地址排序开始")
        tempAddList = []
        tempSpeedList = []
        proxyAddrSpeedList.sort()
        for p1 in proxyAddrSpeedList:
            tempSpeedList.append(p1.split("|")[0])
            tempAddList.append(p1.split("|")[1])
            print(p1.split("|")[1])
        print("speed = %s" % (",".join(tempSpeedList)))
        # 输出：逗号分隔的代理地址
        print("proxyAddressArray = %s" % (",".join(tempAddList)))
        print("已测试地址排序结束")
if __name__=='__main__':
    #test_main(proxyAddressArray)
    gou = get_country('http://225.104.14.7:42119')
    print(gou)