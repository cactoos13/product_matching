import os
from datetime import datetime
from typing import Type, List

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


    def create_minhash(self, text: str) -> MinHash:
        m = MinHash(self.lsh.h)
        for token in text.split():
            m.update(token.encode('utf-8'))
        return m


    def query(self, text: str) -> [int]:
        minhash = self.create_minhash(text)
        return self.lsh.query(minhash)


    def save(self, entity: AdvertisementIdx):
        minhash = self.create_minhash(entity.text)
        self.lsh.insert(entity.id, minhash)
        ad_idx_prefix = os.getenv('ADS_REDIS_INDEX_PREFIX')
        entity_id = str(entity.id)

        if ad_idx_prefix:
            entity.id = f"{ad_idx_prefix}_{entity.id}"
        self.redis_client.set(
            entity_id,
            True
        )



    def save_all(self, entities: List[AdvertisementIdx]):
        for entity in entities:
            self.save(entity)


    def update_last_sync(self):
        key = os.getenv('LAST_SYNC_KEY')
        if not key:
            key = 'last_sync'
        self.redis_client.set(key, str(int(datetime.now().timestamp())))


    async def get_last_sync(self)-> datetime | None:
        key = os.getenv('LAST_SYNC_KEY')
        if not key:
            key = 'last_sync'
        result = await self.redis_client.get(key)
        if result:
            return datetime.fromtimestamp(int(result))
        return None




