from __future__ import absolute_import

from .celeryapp import app as celery_app

import pymysql
pymysql.install_as_MySQLdb()
