from typing import List, Awaitable
from datetime import datetime
from packages.business.modules.advertisement.entities import AdvertisementIdx
from packages.business.modules.advertisement.repositories import AdvertisementRedisRepository
from packages.core.service.redis_service import RedisService


class AdvertisementRedisService(RedisService[AdvertisementIdx]):
    def __init__(self, repository: AdvertisementRedisRepository):
        super().__init__(repository)
        self.repository = repository


    def index_ads(self, ads: List[AdvertisementIdx]):
        return self.repository.save_all(ads)


    def query(self, key: str) -> AdvertisementIdx | None:
        return self.repository.query(key)


    def update_last_sync(self):
        return self.repository.update_last_sync()

    async def get_last_sync(self)-> Awaitable[datetime | None]:
        return self.repository.get_last_sync()


