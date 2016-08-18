{% from "saltweb/map.jinja" import saltweb with context %}

#!/usr/bin/env python

import requests
import json
import sys
import re
import redis

def getInfo():
    #return "hello world"
    redis_host = '{{ saltweb.app.redis.host }}'
    redis_port = {{ saltweb.app.redis.port }}
    redis_pswd = {{ saltweb.app.redis.password }}
    redis_r = redis.StrictRedis(host=redis_host,
                                port=redis_port,
                                password=redis_pswd,
                                db=0)
    rev = None

    username = '{{ saltweb.app.salt_api.username }}'
    password = '{{ saltweb.app.salt_api.password }}'
    proto = '{{ saltweb.app.salt_api.proto }}'
    host = '{{ saltweb.app.salt_api.host }}'
    port = '{{ saltweb.app.salt_api.port }}'
    payload_auth = {'username': username, 'password': password, 'eauth': 'pam'}
    headers = {'Accept': 'application/json'}
    applications = set()
    mineget_srv = '{{ saltweb.app.mineget_srv }}'

    payload = {'client': 'local',
               'tgt': mineget_srv,
               'expr_form': 'compound',
               'fun': 'mine.get',
               'arg': ['G@applications:* and G@roles:webserver','network.ip_addrs', "compound"],
               'username': username,
               'password': password,
               'eauth': 'pam',
               'timeout': '2'}
    r = requests.post(proto+'://' + host + ':' + port + '/run',
                      data=payload,
                      headers=headers,
                      verify=False)
    srvs = ""
    for srv in r.json()['return'][0][mineget_srv]:
        srvs += srv+","

    payload = {'client': 'local',
               'tgt': srvs, #'G@applications:* and G@roles:webserver',
               'expr_form': 'list',
               'fun': 'jp_api.info',
               'username': username,
               'password': password,
               'eauth': 'pam',
               'timeout': '2'}
    r = requests.post(proto+'://' + host + ':' + port + '/run',
                      data=payload,
                      headers=headers,
                      verify=False)
    rjson = r.json()
    # print json.dumps(r.json()['return'][0], indent=2, sort_keys=True)

    for srv in rjson['return'][0]:
        if not isinstance(rjson['return'][0][srv], basestring):
            for app in rjson['return'][0][srv]:
                applications.add(app)
                print app

    result = []
    for app in applications:
        for srv in rjson['return'][0]:
            if app in rjson['return'][0][srv]:
                for env in rjson['return'][0][srv][app]:
                    if len(rjson['return'][0][srv][app][env]) > 0:
                        for repo in  rjson['return'][0][srv][app][env][0]:
                            try:
                                rev = redis_r.hget(app,
                                                   repo+':'+env+':'+app)
                            except:
                                pass
                            if rjson['return'][0][srv][app][env][0][repo][3]:
                                extpillar = True
                            else:
                                extpillar = False
                            result.append({'app':app,
                                           'srv':srv,
                                           'env':env,
                                           'repo':repo,
                                           'rev_server':rjson['return'][0][srv][app][env][0][repo][0],
                                           'rev':rev,
                                           'repo_id':rjson['return'][0][srv][app][env][0][repo][2],
                                           'extpillar_used':extpillar,
                                           'target':rjson['return'][0][srv][app][env][0][repo][1].replace("/", ":")[1:]})
                            rev = ''

#    print json.dumps(result, sort_keys=True,
#                     indent=2, separators=(',', ': '))
    # Logout
    r = requests.post(proto+'://' + host + ':' + port + '/logout', verify=False)

    return json.dumps(result, sort_keys=True,
                     indent=2, separators=(',', ': '))
#getInfo()
def git_rev(app, key, rev):
    #return "hello world"
    redis_host = '{{ saltweb.app.redis.host }}'
    redis_port = {{ saltweb.app.redis.port }}
    redis_pswd = {{ saltweb.app.redis.password }}
    redis_r = redis.StrictRedis(host=redis_host,
                                port=redis_port,
                                password=redis_pswd,
                                db=0)

    rev = redis_r.hset(app, key, rev)
    return 'OK'

def delete_repo(app, key):
    #return "hello world"
    redis_host = '{{ saltweb.app.redis.host }}'
    redis_port = {{ saltweb.app.redis.port }}
    redis_pswd = {{ saltweb.app.redis.password }}
    redis_r = redis.StrictRedis(host=redis_host,
                                port=redis_port,
                                password=redis_pswd,
                                db=0)

    rev = redis_r.hdel(app, key)
    return 'OK'

def repo_update(repo, srv, repo_id):
    username = '{{ saltweb.app.salt_api.username }}'
    password = '{{ saltweb.app.salt_api.password }}'
    proto = '{{ saltweb.app.salt_api.proto }}'
    host = '{{ saltweb.app.salt_api.host }}'
    port = '{{ saltweb.app.salt_api.port }}'
    payload_auth = {'username': username, 'password': password, 'eauth': 'pam'}
    headers = {'Accept': 'application/json'}
    applications = set()

    payload1 = {'client': 'local',
                'tgt': srv,
                'fun': 'saltutil.pillar_refresh',
                'username': username,
                'password': password,
                'eauth': 'pam',
                'timeout': '2',
                'queue': True}

    payload2 = {'client': 'local',
                'tgt': srv,
                'fun': 'state.sls',
                'arg': [repo+'_repo'],
                'username': username,
                'password': password,
                'eauth': 'pam',
                'timeout': '2',
                'queue': True}

    payload3 = {'client': 'local',
                'tgt': srv,
                'fun': 'state.sls',
                'arg': ['files'],
                'username': username,
                'password': password,
                'eauth': 'pam',
                'timeout': '2',
                'queue': True}
    try:
        print requests.post(proto+'://' + host + ':' + port + '/run',
                      data=payload1,
                      headers=headers,
                      verify=False)

        print requests.post(proto+'://' + host + ':' + port + '/run',
                            data=payload2,
                            headers=headers,
                            verify=False)
        print requests.post(proto+'://' + host + ':' + port + '/run',
                            data=payload3,
                            headers=headers,
                            verify=False)
        requests.post(proto+'://' + host + ':' + port + '/logout', verify=False)
    except:
        pass

    return 'OK'


def git_update(branch):
    username = '{{ saltweb.app.salt_api.username }}'
    password = '{{ saltweb.app.salt_api.password }}'
    proto = '{{ saltweb.app.salt_api.proto }}'
    host = '{{ saltweb.app.salt_api.host }}'
    port = '{{ saltweb.app.salt_api.port }}'
    payload_auth = {'username': username, 'password': password, 'eauth': 'pam'}
    headers = {'Accept': 'application/json'}
    applications = set()

    payload1 = {'client': 'local',
                'tgt': 'G@environment:'+branch,
                'tgt_type': 'compound',
                'fun': 'saltutil.pillar_refresh',
                'username': username,
                'password': password,
                'eauth': 'pam',
                'queue': True}

    payload2 = {'client': 'local',
                'tgt': 'G@environment:'+branch,
                'tgt_type': 'compound',
                'fun': 'state.sls',
                'arg': ['git_repo'],
                'username': username,
                'password': password,
                'eauth': 'pam',
                'queue': True}

    payload3 = {'client': 'local',
                'tgt': 'G@environment:'+branch,
                'tgt_type': 'compound',
                'fun': 'state.sls',
                'arg': ['files'],
                'username': username,
                'password': password,
                'eauth': 'pam',
                'queue': True}
    try:
        print requests.post(proto+'://' + host + ':' + port + '/run',
                      data=payload1,
                      headers=headers,
                      verify=False)

        print requests.post(proto+'://' + host + ':' + port + '/run',
                            data=payload2,
                            headers=headers,
                            verify=False)
        print requests.post(proto+'://' + host + ':' + port + '/run',
                            data=payload3,
                            headers=headers,
                            verify=False)
        requests.post(proto+'://' + host + ':' + port + '/logout', verify=False)
    except:
        pass

    return 'OK'
