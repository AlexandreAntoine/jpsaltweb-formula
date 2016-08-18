# -*- coding: utf-8 -*-
# vim: ft=sls

{% from "saltweb/map.jinja" import saltweb with context %}

{% if saltweb.apache is defined %}
saltweb-apache-service:
  service.running:
    - name: apache2
    - enable: True
    - watch:
      - file: saltweb-apache-config
{% endif %}

saltweb-uwsgi-service:
  service.running:
    - name: uwsgi
    - enable: True
    - watch:
      - file: saltweb-uwsgi-config
      - file: saltweb-bottle-api
      - file: saltweb-bottle-api-get
