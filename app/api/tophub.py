from . import api
from app import redis_store
from flask import jsonify, request
import json
from datetime import timedelta, timezone, datetime



def convert_utc8(timestamp):
    utc8 = timezone(timedelta(hours=8))
    t = datetime.fromtimestamp(int(float(timestamp))).replace(tzinfo=timezone.utc)
    return t.astimezone(utc8)


@api.route('/tophub/reddit')
def redis_items():
    data = redis_store.lrange('reddit:data', 0, -1)
    timestamp = redis_store.get('reddit:timestamp')
    return jsonify({
        'update_timestamp': timestamp.decode('utf-8'),
        'data': [json.loads(d.decode('utf-8')) for d in data]
    })


@api.route('/tophub/douban')
def douban_items():
    # 分虚构类和非虚构类通过`subcat` query string判断 默认虚构类
    data = redis_store.lrange('douban_book_fiction:data', 0, -1)
    timestamp = redis_store.get('douban_book_fiction:timestamp')
    if request.args.get('subcat', None) == 'I':
        data = redis_store.lrange('douban_book_non_fiction:data', 0, -1)
        timestamp = redis_store.get('douban_book_non_fiction:timestamp')
    return jsonify({
        'update_timestamp': timestamp.decode('utf-8'),
        'data': [json.loads(d.decode('utf-8')) for d in data]
    })


@api.route('/tophub/juejin')
def juejin_items():
    data = redis_store.lrange('juejin:data', 0, -1)
    timestamp = redis_store.get('juejin:timestamp')
    return jsonify({
        'update_timestamp': timestamp.decode('utf-8'),
        'data': [json.loads(d.decode('utf-8')) for d in data]
    })


@api.route('/tophub/github')
def github_items():
    data = redis_store.lrange('github:data', 0, -1)
    timestamp = redis_store.get('github:timestamp')
    return jsonify({
        'update_timestamp': timestamp.decode('utf-8'),
        'data': [json.loads(d.decode('utf-8')) for d in data]
    })


@api.route('/tophub/segmentfault')
def segmentfault_items():
    data = redis_store.lrange('segmentfault:data', 0, -1)
    timestamp = redis_store.get('segmentfault:timestamp')
    return jsonify({
        'update_timestamp': timestamp.decode('utf-8'),
        'data': [json.loads(d.decode('utf-8')) for d in data]
    })

