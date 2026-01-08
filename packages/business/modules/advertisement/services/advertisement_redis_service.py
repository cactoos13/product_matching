from typing import List, Awaitable
from datetime import datetime
from packages.business.modules.advertisement.entities import AdvertisementIdx
from packages.business.modules.advertisement.repositories import AdvertisementRedisRepository
from packages.core.service.redis_service import RedisService


class AdvertisementRedisService(RedisService[AdvertisementIdx]):
    def __init__(self, repository: AdvertisementRedisRepository):
        super().__init__(repository)
        self.repository = repository


    def index_ads(self, ads: List[AdvertisementIdx], batch_size: int = 32):
        """Index advertisements using ParsBERT embeddings"""
        return self.repository.save_all(ads, batch_size=batch_size)


    def query(self, text: str, limit: int = 10, min_similarity: float = 0.0) -> List[int]:
        """
        Find similar products using ParsBERT embeddings.
        
        Args:
            text: Query text to search for
            limit: Maximum number of products to return
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
        
        Returns:
            List of product IDs sorted by similarity (highest first)
        """
        return self.repository.query(text, limit=limit, min_similarity=min_similarity)
    
    def query_with_scores(self, text: str, limit: int = 10, min_similarity: float = 0.0) -> List[tuple[int, float]]:
        """
        Find similar products using ParsBERT embeddings with similarity scores.
        
        Args:
            text: Query text to search for
            limit: Maximum number of products to return
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
        
        Returns:
            List of tuples: (product_id, similarity_score) sorted by similarity (highest first)
        """
        return self.repository.query_with_scores(text, limit=limit, min_similarity=min_similarity)


    def update_last_sync(self):
        return self.repository.update_last_sync()

    async def get_last_sync(self)-> Awaitable[datetime | None]:
        return self.repository.get_last_sync()


