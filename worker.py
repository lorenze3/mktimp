# -*- coding: utf-8 -*-
"""
Created on Sat May 12 14:12:18 2018

@author: TeamLorenzen
"""

import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

redisconn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(redisconn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()