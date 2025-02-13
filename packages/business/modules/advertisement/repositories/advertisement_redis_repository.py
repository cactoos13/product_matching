from packages.business.modules.advertisement.entities.advertisement_idx_entity import AdvertisementIdx
from packages.core.repository.redis_repository import RedisRepository


class AdvertisementRedisRepository(RedisRepository[AdvertisementIdx]):
    pass

