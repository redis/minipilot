#!/bin/sh

export FLASK_APP=src/application.py
export FLASK_DEBUG=1
export PYTHONPATH=src/

#gunicorn --workers 1 --bind 0.0.0.0:5009 --threads 4 "wsgi:create_app()"
#gunicorn --workers 1 --bind 0.0.0.0:5000 --log-file /var/log/keybase/rediskb.log --log-level INFO "wsgi:create_app()"
flask run --host=0.0.0.0 --port=5005 &
