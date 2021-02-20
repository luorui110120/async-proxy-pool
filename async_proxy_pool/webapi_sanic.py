#!/usr/bin/env python
# coding=utf-8

from sanic import Sanic
from sanic.response import json

#from async_proxy_pool.database import RedisClient
from async_proxy_pool.data_sqlite3 import SQLite3Client

app = Sanic()
sqlite3_conn = SQLite3Client()


@app.route("/")
async def index(request):
    return json({"Welcome": "This is a proxy pool system."})


@app.route("/pop")
async def pop_proxy(request):
    proxy = sqlite3_conn.pop_proxy()
    if proxy[:5] == "https":
        return json({"https": proxy})
    else:
        return json({"http": proxy})


@app.route("/get/<count:int>")
async def get_proxy(request, count):
    res = []
    for proxy in sqlite3_conn.get_proxies(count):
        if proxy[:5] == "https":
            res.append({"https": proxy})
        else:
            res.append({"http": proxy})
    return json(res)


@app.route("/count")
async def count_all_proxies(request):
    count = sqlite3_conn.count_all_proxies()
    return json({"count": str(count)})


@app.route("/count/<score:int>")
async def count_score_proxies(request, score):
    count = sqlite3_conn.count_score_proxies(score)
    return json({"count": str(count)})


@app.route("/clear/<score:int>")
async def clear_proxies(request, score):
    if sqlite3_conn.clear_proxies(score):
        return json({"Clear": "Successful"})
    return json({"Clear": "Score should >= 0 and <= 10"})
