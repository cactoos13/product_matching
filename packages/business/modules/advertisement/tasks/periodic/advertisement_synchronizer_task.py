from packages.core.scheduler.task import PeriodicTask
from celery.schedules import crontab

class AdvertisementSynchronizerTask(PeriodicTask):

    def get_schedule(self) -> crontab:
        return crontab('*')

    def get_name(self) -> str:
        return 'advertisement_synchronizer_task'

    def get_args(self):
        return "arg1", "arg2"

    def get_kwargs(self):
        return ()


    def run(self, *args, **kwargs):
        print("my args:", args)
        print("Hello from AdvertisementSynchronizerTask")