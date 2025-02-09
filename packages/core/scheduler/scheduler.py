from typing import Self
from celery import Celery

from packages.core.install import Installable
from packages.core.scheduler.task import PeriodicTask


class SchedulerConfig:
    def __init__(self):
        self.broker_url = ''
        self.result_backend = ''
        self.task_serializer = 'json'
        self.result_serializer = 'json'
        self.accept_content = ['json']
        self.timezone = 'GMT'

    def set_broker_url(self, url)-> Self:
        self.broker_url = url
        return self

    def set_result_backend(self, url)-> Self:
        self.result_backend = url
        return self

    def set_task_serializer(self, serializer)-> Self:
        self.task_serializer = serializer
        return self

    def set_result_serializer(self, serializer)-> Self:
        self.result_serializer = serializer
        return self

    def set_accept_content(self, content)-> Self:
        self.accept_content = content
        return self

    def set_timezone(self, timezone)-> Self:
        self.timezone = timezone
        return self

    def get_broker_url(self):
        return self.broker_url

    def get_result_backend(self):
        return self.result_backend

    def get_task_serializer(self):
        return self.task_serializer

    def get_result_serializer(self):
        return self.result_serializer

    def get_accept_content(self):
        return self.accept_content

    def get_timezone(self):
        return self.timezone



class Scheduler(Celery):

    def __init__(self, config: SchedulerConfig):
        super().__init__('scheduler')
        self.celery = Celery(
            "task_scheduler",
            broker=config.get_broker_url(),
            backend=config.get_result_backend(),
        )
        self.celery.conf.task_serializer = config.get_task_serializer()
        self.celery.conf.result_serializer = config.get_result_serializer()
        self.celery.conf.accept_content = config.get_accept_content()
        self.celery.conf.timezone = config.get_timezone()

    def get_app(self):
        return self.celery


    def register_periodic_task(self, task: PeriodicTask):
        self.celery.conf.beat_schedule = {
            task.task_name: {
                "task": task.run,
                "schedule": task.schedule,
                "args": task.task_args,
            },
        }



