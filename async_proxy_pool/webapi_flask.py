#!/usr/bin/env python
# coding=utf-8

from flask import Flask, jsonify
#from async_proxy_pool.database import RedisClient
from async_proxy_pool.data_sqlite3 import SQLite3Client

app = Flask(__name__)
sqlite3_conn = SQLite3Client()


@app.route("/")
def index():
    return jsonify({"Welcome": "This is a proxy pool system."},
                   {"api": "pop , get"})


@app.route("/pop")
def pop_proxy():
    proxy = sqlite3_conn.pop_proxy()
    if proxy[:5] == "https":
        return jsonify({"https": proxy})
    else:
        return jsonify({"http": proxy})


@app.route("/get/<int:count>")
def get_proxy(count):
    res = []
    for proxy in sqlite3_conn.get_proxies(count):
        if proxy[:5] == "https":
            res.append({"https": proxy})
        else:
            res.append({"http": proxy})
    return jsonify(res)


@app.route("/count")
def count_all_proxies():
    count = sqlite3_conn.count_all_proxies()
    return jsonify({"count": str(count)})


@app.route("/count/<int:score>")
def count_score_proxies(score):
    count = sqlite3_conn.count_score_proxies(score)
    return jsonify({"count": str(count)})


@app.route("/clear/<int:score>")
def clear_proxies(score):
    if sqlite3_conn.clear_proxies(score):
        return jsonify({"Clear": "Successful"})
    return jsonify({"Clear": "Score should >= 0 and <= 10"})
