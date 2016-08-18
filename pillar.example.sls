saltweb:
  apache:
    config: /etc/apache2/sites-enabled/saltweb-apache.conf
    domain: exemple.fr
  uwsgi:
    config: /etc/uwsgi/apps-enabled/saltweb-uwsgi.ini
  app:
    mineget_srv: XXX
    git:
      url: https://github.com/AlexandreLoman/jpsaltweb-app.git
      remote: origin
      branch: master
    path: /srv/www/saltweb
    web_front:
      api:
        host: XXX.XXX.XXX.XXX
        port: 80
    web_api:
      bind: 0.0.0.0
      apikey: secret
    redis:
      host: XXX.XXX.XXX.XXX
      port: 6379
      password: None
    salt_api:
      username: salt-api
      password: password
      proto: http
      host: XXX.XXX.XXX.XXX
      port: XXX
    users:
      toto:
        password: toto
        write: False
      admin:
        password: admin
        write: True
      hello:
        password: hello
        write: True
    deleteusers:
      - toto
