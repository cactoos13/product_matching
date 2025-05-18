from datetime import datetime
from packages.business.modules.advertisement.services import AdvertisementSqlService
from packages.business.modules.advertisement.services.advertisement_redis_service import AdvertisementRedisService
from packages.business.modules.system_task.entities import SystemTask, SystemTaskTypeEnum, SystemTaskStatusEnum
from packages.business.modules.system_task.services import SystemTaskSqlService
from packages.core.registry import Registry
from packages.core.scheduler.task import Task



class AdvertisementBatchIndex:
    def __init__(
            self,
            offset: int,
            limit: int,
            start: datetime,
            end: datetime,
    ):
        self.offset = offset
        self.limit = limit
        self.start = start
        self.end = end

    def get_ads(self):
        ad_service = Registry().get(AdvertisementSqlService)
        ads = ad_service.get_changed_ads(
            start_date=self.start,
            end_date=self.end,
            offset=self.offset,
            limit=self.limit
        )
        return ads

    def execute(self):
        ad_redis_service = Registry().get(AdvertisementRedisService)
        print(f"Indexing ads with offset {self.offset} and limit {self.limit}")
        ads = self.get_ads()
        ad_redis_service.index_ads(ads)





class AdvertisementBatchIndexTask(Task):
    def get_name(self) -> str:
        return 'advertisement_batch_index_task'

    def run(self, *args, **kwargs):
        offset = kwargs.get('offset')
        limit = kwargs.get('limit')
        start = kwargs.get('start')
        end = kwargs.get('end')
        parent_task_id = kwargs.get('parent_task_id')

        sys_task_service = Registry().get(SystemTaskSqlService)
        sys_task = SystemTask(
            type=SystemTaskTypeEnum.INDEX_ADVERTISEMENTS_WORKER,
            status=SystemTaskStatusEnum.PENDING,
            name='Index ads worker',
            parent_id=parent_task_id
        )
        sys_task = sys_task_service.save(sys_task)

        try:
            batch_index = AdvertisementBatchIndex(
                offset= offset,
                limit= limit,
                start= start,
                end = end,
            )
            batch_index.execute()
        except Exception as e:
            sys_task_service.fail_the_task(sys_task)
            parent_task = sys_task_service.get_by_id(parent_task_id)
            parent_task.status = SystemTaskStatusEnum.FAILED
            sys_task_service.save(parent_task)
            print(f"Error in indexing ads: {e}")
            return False
        print("Indexing ads done")
        sys_task_service.done_the_task(sys_task)
        return True