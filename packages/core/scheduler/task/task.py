from abc import abstractmethod, ABC
from celery.schedules import crontab

from celery import Task as CeleryTask
class Task(CeleryTask, ABC):

    @property
    def name(self):
        return self.get_name()

    @abstractmethod
    def get_name(self)-> str:
        pass


    @abstractmethod
    def get_args(self)-> tuple:
        pass

    @abstractmethod
    def get_kwargs(self)-> dict:
        pass


    @abstractmethod
    def run(self, *args, **kwargs):
        pass




class PeriodicTask(Task, ABC):

    @abstractmethod
    def get_schedule(self)-> crontab:
        pass


