from packages.business.modules.advertisement.entities import AdvertisementIdx
from packages.business.modules.advertisement.repositories import AdvertisementRedisRepository
from packages.core.service.redis_service import RedisService


class AdvertisementRedisService(RedisService[AdvertisementIdx]):
    def __init__(self, repository: AdvertisementRedisRepository):
        super().__init__(repository)
        self.repository = repository


    def index_ads(self, ads: [AdvertisementIdx]):
        return self.repository.save_all(ads)


    def query(self, key: str) -> AdvertisementIdx | None:
        return self.repository.query(key)


