#!/bin/sh
flask db upgrade
#flask run
exec gunicorn -b :5000 --access-logfile - --error-logfile - bvb02:app
