from abc import abstractmethod, ABC
from typing import Self
from celery.schedules import crontab


class Task:
    def __init__(
        self,
        task_name: str = None,
        task_args: tuple = None,
    ):
        self.task_name = task_name
        self.task_args = task_args
        self.kwargs = None

    @abstractmethod
    def run(self):
        pass




class PeriodicTask(Task, ABC):
    def __init__(self, schedule: crontab):
        super().__init__()
        self.schedule = schedule

