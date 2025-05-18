from datetime import datetime

from celery.schedules import crontab
from packages.business.modules.advertisement.services import AdvertisementSqlService
from packages.business.modules.advertisement.services.advertisement_redis_service import AdvertisementRedisService
from packages.business.modules.advertisement.tasks.once import AdvertisementBatchIndexTask
from packages.business.modules.system_task.entities import SystemTask, SystemTaskTypeEnum, SystemTaskStatusEnum
from packages.business.modules.system_task.services import SystemTaskSqlService
from packages.core.registry import Registry
from packages.core.scheduler import Scheduler
from packages.core.scheduler.task import PeriodicTask


class AdvertisementIndexerTask(PeriodicTask):

    def get_schedule(self) -> crontab:
        return crontab(
            minute='*',
            nowfun=datetime.now
        )

    def get_name(self) -> str:
        return 'advertisement_indexer_task'

    def get_args(self):
        return ()

    def get_kwargs(self):
        return ()

    async def run(self, *args, **kwargs):
        ad_service = Registry().get(AdvertisementSqlService)

        ad_redis_service = Registry().get(AdvertisementRedisService)
        last_sync = await ad_redis_service.get_last_sync()
        if not last_sync:
            print("Redis storage is wiped out, synchronizing all ads")
            last_sync = datetime(1970, 1, 1)

        print(f"Last sync was at {last_sync}")
        now = datetime.now()
        not_indexed_count = ad_service.get_changed_ads_count(
            start_date=last_sync,
            end_date=now
        )
        if not_indexed_count == 0:
            print("No ads to index")
            return

        print(f"Found {not_indexed_count} ads not indexed yet")


        sys_task_service = Registry().get(SystemTaskSqlService)
        sys_task = SystemTask(
            type=SystemTaskTypeEnum.INDEX_ADVERTISEMENTS,
            status=SystemTaskStatusEnum.PENDING,
            name='Index ads'
        )
        sys_task = sys_task_service.save(sys_task)

        print("Planning to index ads...")
        batch = 100

        scheduler = Registry().get(Scheduler)
        for i in range(0, 200, batch):
            print(f"Planning to Index ads from {i} to {i + batch}")
            task = AdvertisementBatchIndexTask(
                offset=i,
                limit=batch,
                start=last_sync,
                end=now,
                parent_task_id=sys_task.id
            )
            scheduler.run_task(task)
        sys_task_service.done_the_task(sys_task)
        print("Planning to index ads... Done")
