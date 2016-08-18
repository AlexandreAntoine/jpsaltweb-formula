{% from "saltweb/map.jinja" import saltweb with context %}

#!/usr/bin/env python

import bottle
import hashlib
from api import getapp3
import json
import jwt
import base64
import os
import redis

from bottle import  request, response
from datetime import datetime
from functools import wraps
import logging

logger = logging.getLogger('myapp')

# set up the logger
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('/var/log/saltweb/saltweb3.log')
formatter = logging.Formatter('%(msg)s')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_to_logger(fn):
    '''
    Wrap a Bottle request so that a log line is emitted after it's handled.
    (This decorator can be extended to take the desired logger as a param.)
    '''
    @wraps(fn)
    def _log_to_logger(*args, **kwargs):
        request_time = datetime.now()
        actual_response = fn(*args, **kwargs)
        # modify this to log exactly what you need:
        try:
            auth = bottle.request.headers.get('Authorization', None)
            parts = auth.split()
            token = parts[1]
            _user = jwt.decode(
                token,
                '{{saltweb.app.web_api.apikey}}'
            )
            username =  _user['username']
        except:
            username = ""
        logger.info('%s %s %s %s %s %s' % (request.remote_addr,
                                           request_time,
                                           request.method,
                                           request.url,
                                           response.status,
                                           username))
        return actual_response
    return _log_to_logger


app = application  = bottle.Bottle()
app.install(log_to_logger)
_user = None

def authenticate(error):
  bottle.abort(500, "Sorry, access denied.")
  return error

def requires_auth(f):
  def decorated(*args, **kwargs):
    auth = bottle.request.headers.get('Authorization', None)
    if not auth:
      return authenticate({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
    elif len(parts) == 1:
      return {'code': 'invalid_header', 'description': 'Token not found'}
    elif len(parts) > 2:
      return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}

    token = parts[1]
    try:
       _user = jwt.decode(
            token,
          '{{saltweb.app.web_api.apikey}}'
        )
    except jwt.ExpiredSignature:
        return authenticate({'code': 'token_expired', 'description': 'token is expired'})
    except jwt.InvalidAudienceError:
        return authenticate({'code': 'invalid_audience', 'description': 'incorrect audience, expected: YOUR_CLIENT_ID'})
    except jwt.DecodeError:
        return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})
    return f(*args, **kwargs)

  return decorated

def requires_right(f):
  def decorated(*args, **kwargs):
    auth = bottle.request.headers.get('Authorization', None)
    parts = auth.split()
    token = parts[1]
    try:
       _user = jwt.decode(
            token,
          '{{saltweb.app.web_api.apikey}}'
        )
       if _user['write'] != 'True':
         return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})
    except:
        return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})
    return f(*args, **kwargs)
  return decorated

@app.hook('after_request')
def enable_cors():
    bottle.response.headers['Access-Control-Allow-Origin'] = '*'

@app.post('/authenticate')
def auth():
    redis_host = '{{ saltweb.app.redis.host }}'
    redis_port = {{ saltweb.app.redis.port }}
    redis_pswd = {{ saltweb.app.redis.password }}
    redis_r = redis.StrictRedis(host=redis_host,
                                port=redis_port,
                                password=redis_pswd,
                                db=0)

    password = request.json['password']
    username = request.json['username']

    try:
      pswd = redis_r.hget('users_'+username,
                          "password")
      write = redis_r.hget('users_'+username,
                          "write")
    except:
      return "error"

    if pswd != None and pswd == password:
      return { 'token' : jwt.encode({'username': username, 'password': password, 'write': write}, '{{saltweb.app.web_api.apikey}}', algorithm='HS256'), 'write': write }
    else:
      return "error"

@app.route('/info')
@requires_auth
def getinfo():
  return getapp3.getInfo()

@app.put('/git/<srv>/<repo_id>/<app>/<key>/<rev>')
@requires_auth
@requires_right
def repo_rev(srv, repo_id, app, key, rev):
  getapp3.git_rev(app, key, rev)
  getapp3.repo_update("git", srv, repo_id)

@app.put('/svn/<srv>/<repo_id>/<app>/<key>/<rev>')
@requires_auth
@requires_right
def repo_rev(srv, repo_id, app, key, rev):
  getapp3.git_rev(app, key, rev)
  getapp3.repo_update("svn", srv, repo_id)

@app.delete('/git/<srv>/<repo_id>/<app>/<key>')
@requires_auth
@requires_right
def repo_rev(srv, repo_id, app, key):
  getapp3.delete_repo(app, key)

@app.delete('/svn/<srv>/<repo_id>/<app>/<key>')
@requires_auth
@requires_right
def repo_rev(srv, repo_id, app, key):
  getapp3.delete_repo(app, key)

# @app.route('/git/<srv>/<repo_id>', method="PATCH")
# @requires_auth
# @requires_right
# def repo_rev(srv, repo_id):
#   getapp3.repo_update("git", srv, repo_id)

# @app.route('/svn/<srv>/<repo_id>', method="PATCH")
# @requires_auth
# @requires_right
# def repo_rev(srv, repo_id):
#   getapp3.repo_update("svn", srv, repo_id)

@app.post('/github')
def auth():
    branch = request.json['ref'].split('/')[2]
    appName = request.json['repository']['name']
    logger.info(json.dumps(request.json))

    if branch == "test":
        getapp3.git_update(branch)

    return "OK"

if __name__ == '__main__':
    app.run(application=app, host='{{saltweb.app.web_api.bind}}', port=8001, debug=True)
