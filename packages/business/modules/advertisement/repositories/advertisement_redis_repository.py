from typing import Type, List

from datasketch import MinHashLSH, MinHash
from redis import Redis
from packages.business.modules.advertisement.entities.advertisement_idx_entity import AdvertisementIdx
from packages.core.registry import Registry
from packages.core.repository.redis_repository import RedisRepository
from sklearn.feature_extraction.text import CountVectorizer

class AdvertisementRedisRepository(RedisRepository[AdvertisementIdx]):
    def __init__(self, entity: Type[AdvertisementIdx], redis_client: Redis):
        super().__init__(entity, redis_client)
        self.redis_client = redis_client
        self.entity = entity
        self.lsh = Registry().get(MinHashLSH)
        self.vectorizer = Registry().get(CountVectorizer)


    def create_minhash(self, text: str) -> MinHash:
        print(self.lsh.h)
        m = MinHash(self.lsh.h)
        for token in text.split():
            m.update(token.encode('utf-8'))
        return m


    def query(self, text: str) -> [int]:
        print("Querying\n", text)

        minhash = self.create_minhash(text)
        return self.lsh.query(minhash)


    def save(self, entity: AdvertisementIdx):
        minhash = self.create_minhash(entity.text)
        self.lsh.insert(entity.id, minhash)

    def save_all(self, entities: List[AdvertisementIdx]):
        for entity in entities:
            self.save(entity)



