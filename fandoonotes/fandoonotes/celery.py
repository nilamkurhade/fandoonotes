from __future__ import absolute_import
from celery import Celery

app = Celery('test_celery',
             broker='amqp://admin:admin@1234@localhost/admin_vhost',
             backend='rpc://',
             include=['test_celery.tasks'])
