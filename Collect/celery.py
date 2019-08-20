from __future__ import absolute_import

from celery import Celery
from django.conf import settings

import os

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Collect.settings')
# app = Celery('Collect', backend='rpc://', broker='amqp://guest:guest@localhost:5672')
app = Celery('Collect')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))