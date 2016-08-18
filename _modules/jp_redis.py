# -*- coding: utf-8 -*-

"""
redis
"""

import logging
import redis

log = logging.getLogger(__name__)

def adduser(host, port, pswd, user, password, write):
    data = None
    if True:
        if pswd == "None":
            pswd = ""
        r = redis.StrictRedis(host=host, port=port, password=pswd, db=0)
        res = ''

        try:
            data = r.hset('users_'+user, 'password', password)
            log.info(data)
            data = r.hset('users_'+user, 'write', write)
            log.info(data)
        except:
            pass
    return data

def deleteuser(host, port, pswd, user):
    data = None
    if True:
        if pswd == "None":
            pswd = ""
        r = redis.StrictRedis(host=host, port=port, password=pswd, db=0)
        res = ''

        try:
            data = r.hdel('users_'+user, 'password', 'write')
            log.info(data)
        except:
            pass
    return data
