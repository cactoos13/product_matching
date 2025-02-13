from typing import Type

from datasketch import MinHashLSH, MinHash
from redis import Redis
from packages.business.modules.advertisement.entities.advertisement_idx_entity import AdvertisementIdx
from packages.core.registry import Registry
from packages.core.repository.redis_repository import RedisRepository

class AdvertisementRedisRepository(RedisRepository[AdvertisementIdx]):
    def __init__(self, entity: Type[AdvertisementIdx], redis_client: Redis):
        super().__init__(entity, redis_client)
        self.redis_client = redis_client
        self.entity = entity
        self.lsh = Registry().get(MinHashLSH)


    def query(self, key: str) -> [int]:
        m = MinHash(self.lsh.h)
        m.update(key.encode('utf-8'))
        result = self.lsh.query(m)
        print(result)
        return result

    def save(self, entity: AdvertisementIdx):
        m = MinHash(self.lsh.h)
        m.update(entity.text.encode('utf-8'))
        self.lsh.insert(entity.id, m)
        return entity

    def save_all(self, entities: [AdvertisementIdx]):
        with self.lsh.insertion_session() as session:
            for entity in entities:
                m = MinHash(self.lsh.h)
                m.update(entity.text.encode('utf-8'))
                session.insert(entity.id, m)

