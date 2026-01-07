from typing import List
from packages.business.modules.advertisement.entities import AdvertisementIdx
from packages.business.modules.advertisement.services.c2c_advertisement_sql_service import C2CAdvertisementSqlService
from packages.business.modules.advertisement.services.advertisement_redis_service import AdvertisementRedisService
from packages.business.modules.system_task.entities import SystemTask, SystemTaskTypeEnum, SystemTaskStatusEnum
from packages.business.modules.system_task.services import SystemTaskSqlService
from packages.core.registry import Registry
from packages.core.scheduler.task import Task



class AdvertisementBatchIndexByCategories:
    def __init__(
            self,
            category_ids: List[int],
            limit: int = None,
            offset: int = None,
    ):
        self.category_ids = category_ids
        self.limit = limit
        self.offset = offset

    def get_ads(self):
        c2c_ad_service = Registry().get(C2CAdvertisementSqlService)
        ads = c2c_ad_service.get_ads_by_category_ids(
            category_ids=self.category_ids,
            limit=self.limit,
            offset=self.offset
        )
        return ads

    def convert_to_idx(self, c2c_ads):
        """Convert C2CAdvertisement entities to AdvertisementIdx for indexing"""
        idx_ads = []
        for ad in c2c_ads:
            # Combine title and description as text for indexing
            text_parts = [ad.title] if ad.title else []
            if ad.description:
                text_parts.append(ad.description)
            text = " ".join(text_parts)
            
            idx_ad = AdvertisementIdx(
                id=ad.id,
                text=text
            )
            idx_ads.append(idx_ad)
        return idx_ads

    def execute(self):
        ad_redis_service = Registry().get(AdvertisementRedisService)
        print(f"Indexing ads for category IDs: {self.category_ids} (limit: {self.limit}, offset: {self.offset})")
        c2c_ads = self.get_ads()
        print(f"Found {len(c2c_ads)} ads to index")
        
        # Convert C2CAdvertisement to AdvertisementIdx
        idx_ads = self.convert_to_idx(c2c_ads)
        ad_redis_service.index_ads(idx_ads)
        print(f"Indexed {len(idx_ads)} ads successfully")




class AdvertisementBatchIndexByCategoriesTask(Task):
    def __init__(
            self,
            *args,
            **kwargs
    ):
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def get_name(self) -> str:
        return 'advertisement_batch_index_by_categories_task'

    def get_args(self):
        return self.args

    def get_kwargs(self):
        return self.kwargs

    def run(self, *args, **kwargs):
        category_ids = kwargs.get('category_ids')
        limit = kwargs.get('limit')
        offset = kwargs.get('offset')
        parent_task_id = kwargs.get('parent_task_id')

        if not category_ids:
            print("Error: category_ids is required")
            return False

        sys_task_service = Registry().get(SystemTaskSqlService)
        sys_task = SystemTask(
            type=SystemTaskTypeEnum.INDEX_ADVERTISEMENTS_WORKER,
            status=SystemTaskStatusEnum.PENDING,
            name=f'Index ads by category IDs: {category_ids}',
            parent_id=parent_task_id
        )
        sys_task = sys_task_service.save(sys_task)

        try:
            category_index = AdvertisementBatchIndexByCategories(
                category_ids=category_ids,
                limit=limit,
                offset=offset
            )
            category_index.execute()
        except Exception as e:
            sys_task_service.fail_the_task(sys_task)
            if parent_task_id:
                parent_task = sys_task_service.get_by_id(parent_task_id)
                parent_task.status = SystemTaskStatusEnum.FAILED
                sys_task_service.save(parent_task)
            print(f"Error in indexing ads by category: {e}")
            import traceback
            traceback.print_exc()
            return False
        print("Indexing ads by category done")
        sys_task_service.done_the_task(sys_task)
        return True

