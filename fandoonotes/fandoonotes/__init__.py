from __future__ import absolute_import
from .celery import app as celery_app
import pymysql
pymysql.install_as_MySQLdb()

__all__= ('celery_app',)

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
