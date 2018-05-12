# -*- coding: utf-8 -*-
"""
Created on Sat May 12 14:19:44 2018

@author: TeamLorenzen
"""

import pandas as pd
import numpy as np
from rq import Queue
from rq.job import Job
from worker import redisconn

q=Queue(connection=redisconn)
filetoread='C:/Users/TeamLorenzen/Documents/App0/static/downloads/Input Template -- File name will be analysis title.csv'
job = q.enqueue_call(
    func=doModel, args=(filetoread,), result_ttl=5000
)
print(job.get_id())