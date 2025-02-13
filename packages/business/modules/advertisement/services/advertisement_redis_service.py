from packages.business.modules.advertisement.entities import AdvertisementIdx
from packages.core.service.redis_service import RedisService


class AdvertisementRedisService(RedisService[AdvertisementIdx]):
    pass