from typing import TypeVar, Type

from packages.core.entity import RedisEntity
from packages.core.repository import Repository
import redis

T = TypeVar('T', bound=RedisEntity)
class RedisRepository(Repository[T]):
    def __init__(self, entity: Type[T], redis_client: Type[redis.Redis]):
        super().__init__(entity)
        self.redis_client = redis_client

