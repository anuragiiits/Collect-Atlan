#!/bin/bash

celery -A Collect worker -l info &
gunicorn --bind 0.0.0.0:8080 Collect.wsgi:application