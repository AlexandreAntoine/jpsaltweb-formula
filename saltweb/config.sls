# -*- coding: utf-8 -*-
# vim: ft=sls

{% from "saltweb/map.jinja" import saltweb with context %}


{% if saltweb.app.git is defined %}

saltweb-git:
  pkg.installed:
    - name: git

saltweb-app:
  git.latest:
    - name: {{ saltweb.app.git.url }}
    - target: {{ saltweb.app.path }}/web-app
    - remote: {{ saltweb.app.git.remote }}
    - branch: {{ saltweb.app.git.branch }}
    - force_checkout: True
    - force_clone: True
    - force_reset: True
    - require:
      - pkg: git

{% endif %}

/var/log/saltweb:
    file.directory:
    - user: www-data
    - group: www-data
    - dir_mode: 755
    - file_mode: 644
    - recurse:
        - user
        - group
        - mode

{% if saltweb.apache is defined %}
saltweb-apache-config:
  file.managed:
    - name: {{ saltweb.apache.config }}
    - template: jinja
    - source: salt://saltweb/files/saltweb-apache.conf
    - mode: 644
    - user: root
    - group: root
{% endif %}

{% if saltweb.uwsgi is defined %}
saltweb-uwsgi-config:
  file.managed:
    - name: {{ saltweb.uwsgi.config }}
    - template: jinja
    - source: salt://saltweb/files/saltweb-uwsgi.ini
    - mode: 644
    - user: root
    - group: root
{% endif %}

saltweb-bottle-api:
  file.managed:
    - name: {{ saltweb.app.path }}/saltweb.py
    - template: jinja
    - source: salt://saltweb/files/saltweb.py
    - mode: 644
    - user: root
    - group: root

saltweb-bottle-api-get:
  file.managed:
    - name: {{ saltweb.app.path }}/api/getapp3.py
    - template: jinja
    - source: salt://saltweb/files/getapp3.py
    - mode: 644
    - user: root
    - group: root
    - require:
        - file: {{ saltweb.app.path }}/api

{{ saltweb.app.path }}/api:
    file.directory:
    - user: www-data
    - group: www-data
    - dir_mode: 755
    - file_mode: 644
    - recurse:
        - user
        - group
        - mode

saltweb-bottle-api-get_init:
  file.touch:
    - name: {{ saltweb.app.path }}/api/__init__.py
    - require:
        - file: {{ saltweb.app.path }}/api

{%- for user, config in salt['pillar.get']('saltweb:app:users').iteritems() %}

saltweb-redis_add_{{user}}:
  module.run:
    - name: jp_redis.adduser
    - host: "{{ salt['pillar.get']('saltweb:app:redis:host') }}"
    - port: {{ salt['pillar.get']('saltweb:app:redis:port') }}
    - pswd: "{{ salt['pillar.get']('saltweb:app:redis:password') }}"
    - user: "{{ user }}"
    - password: "{{ config.password }}"
    - write: "{{ config.write }}"
{%- endfor %}

{%- for user in salt['pillar.get']('saltweb:app:deleteusers') %}

saltweb-redis_delete_{{user}}:
  module.run:
    - name: jp_redis.deleteuser
    - host: "{{ salt['pillar.get']('saltweb:app:redis:host') }}"
    - port: {{ salt['pillar.get']('saltweb:app:redis:port') }}
    - pswd: "{{ salt['pillar.get']('saltweb:app:redis:password') }}"
    - user: "{{ user }}"
{%- endfor %}