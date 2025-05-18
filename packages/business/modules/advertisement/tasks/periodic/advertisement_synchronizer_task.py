import datetime

from sqlalchemy import text
from packages.business.modules.advertisement.tasks.once import AdvertisementBatchUpdateTask
from packages.business.modules.system_task.entities import SystemTask, SystemTaskStatusEnum, SystemTaskTypeEnum
from packages.business.modules.system_task.services import SystemTaskSqlService
from packages.core.registry import Registry
from packages.core.scheduler import Scheduler
from packages.core.scheduler.task import PeriodicTask
from celery.schedules import crontab
from packages.core.sql_connector import SqlConnector


class AdvertisementSynchronizerTask(PeriodicTask):

    def get_schedule(self) -> crontab:
        return crontab(
            minute='*/10',
        )

    def get_name(self) -> str:
        return 'advertisement_synchronizer_task'

    def get_args(self):
        return ()

    def get_kwargs(self):
        return ()

    def get_last_sync(self) -> datetime:
        sys_task_service = Registry().get(SystemTaskSqlService)
        return sys_task_service.get_last_sync().created_at

    def run(self, *args, **kwargs):
        last_sync = self.get_last_sync()
        now = datetime.datetime.now()
        print(f"Last sync was at {last_sync}")

        print("Synchronizing ads...")
        system_task_service = Registry().get(SystemTaskSqlService)
        sys_task = SystemTask(
            type=SystemTaskTypeEnum.SYNCHRONIZE_ADS,
            status=SystemTaskStatusEnum.PENDING,
            name='Synchronize ads'
        )
        sys_task = system_task_service.save(sys_task)


        source_connector = Registry().get(SqlConnector, salt='source')
        session = source_connector.get_session()

        count = session.execute(
            text("SELECT COUNT(*) FROM c2c_advertisements WHERE changed_at >= :start AND changed_at <= :end"),
            {
                'start': last_sync,
                'end': now
            }
        ).fetchone()[0]
        session.close()
        print(f"Found {count} ads to synchronize")

        batch_size = 1000
        scheduler = Registry().get(Scheduler)
        for offset in range(0, count, batch_size):
            task = AdvertisementBatchUpdateTask(
                offset=offset,
                limit=batch_size,
                start=last_sync,
                end=now
            )
            scheduler.run_task(task)

        system_task_service.done_the_task(sys_task)
