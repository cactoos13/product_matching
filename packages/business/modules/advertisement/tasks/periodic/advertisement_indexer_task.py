from datetime import datetime

from celery.schedules import crontab

from packages.business.modules.advertisement.entities import Advertisement, AdvertisementIdx
from packages.business.modules.advertisement.services import AdvertisementSqlService
from packages.business.modules.advertisement.services.advertisement_redis_service import AdvertisementRedisService
from packages.business.modules.system_task.entities import SystemTask, SystemTaskTypeEnum, SystemTaskStatusEnum
from packages.business.modules.system_task.services import SystemTaskSqlService
from packages.core.registry import Registry
from packages.core.scheduler.task import PeriodicTask


class AdvertisementIndexerTask(PeriodicTask):

    def get_schedule(self) -> crontab:
        return crontab(
            minute='*/20',
            nowfun=datetime.now
        )

    def get_name(self) -> str:
        return 'advertisement_indexer_task'

    def get_args(self):
        return ()

    def get_kwargs(self):
        return ()

    def run(self, *args, **kwargs):
        ad_service = Registry().get(AdvertisementSqlService)
        not_indexed_count = ad_service.get_not_lsh_indexed_ads_count()
        print(f"Found {not_indexed_count} ads not indexed yet")

        if not_indexed_count == 0:
            print("No ads to index")
            return

        sys_task_service = Registry().get(SystemTaskSqlService)
        sys_task = SystemTask(
            type=SystemTaskTypeEnum.INDEX_ADVERTISEMENTS,
            status=SystemTaskStatusEnum.PENDING,
            name='Index ads'
        )
        sys_task = sys_task_service.save(sys_task)

        print("Indexing ads...")
        batch = 1000
        ad_redis_service = Registry().get(AdvertisementRedisService)
        for i in range(0, not_indexed_count, batch):
            ads = ad_service.get_not_lsh_indexed_ads(i, batch)
            print(f"Indexing {len(ads)} ads")
            ad_redis_service.index_ads(
                [AdvertisementIdx(ad.id, ad.text) for ad in ads]
            )
            ad_service.index_ads(ads)
            print(f"Indexed {len(ads)} ads")

        sys_task.status = SystemTaskStatusEnum.DONE
        sys_task.done_at = datetime.now()
        sys_task_service.update(sys_task)
        print("Done indexing ads")
