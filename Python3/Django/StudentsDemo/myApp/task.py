
from celery import task, app
from StudentsDemo.celery import app
from celery import shared_task

from celery.task import Task

import time


# @shared_task
# def test_celery_task():
#     time.sleep(5)
#     print('sleep finished............')
#     return 'result'

class TestCeleryTask(Task):
    name = 'test_celery_task'

    def run(self, *args, **kwargs):
        print('starting test_celery task..........')
        time.sleep(5)
        print('test_celery task finished..........')
