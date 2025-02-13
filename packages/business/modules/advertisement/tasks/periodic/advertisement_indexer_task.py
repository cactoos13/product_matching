from celery.schedules import crontab

from packages.core.scheduler.task import PeriodicTask


class AdvertisementIndexerTask(PeriodicTask):
    def get_schedule(self) -> crontab:
        pass

    def get_name(self) -> str:
        pass

    def run(self, *args, **kwargs):
        pass