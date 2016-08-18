# -*- coding: utf-8 -*-
# vim: ft=sls

{% from "saltweb/map.jinja" import saltweb with context %}

saltweb-install-modules:
  module.run:
    - name: saltutil.sync_modules

saltweb-install_bottle:
  pkg.installed:
    - pkgs:
        - uwsgi
        - uwsgi-plugin-python
        - apache2
        - libapache2-mod-uwsgi

saltweb-bottle:
  pip.installed:
    - name: bottle
    - require:
      - pkg: python-pip

saltweb-redis:
  pip.installed:
    - name: redis
    - require:
      - pkg: python-pip

saltweb-PyJWT:
  pip.installed:
    - name: PyJWT
    - require:
      - pkg: python-pip

saltweb-python-pip:
  pkg.installed:
    - name: python-pip
