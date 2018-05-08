# -*- coding: utf-8 -*-
"""
Created on Tue May  8 15:20:18 2018

@author: TeamLorenzen
"""

import mysql.connector
conn = mysql.connector.connect(user='root', password='Pi3141592',
                              host='127.0.0.1',
                              database='BucketList',autocommit=True)
cursor = conn.cursor()
cursor.callproc('sp_createUser',('two','two@two','two'))
for reg in cursor.stored_results():
    msg=reg.fetchall()
    print(msg)