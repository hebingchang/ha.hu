from __future__ import absolute_import

import os
from celery import Celery
from hahu import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hahu.settings')

app = Celery('hahu')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('hahu.settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name='tasks')
