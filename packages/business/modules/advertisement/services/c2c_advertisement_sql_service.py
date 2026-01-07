import datetime
from typing import Type, List, Optional

from packages.business.modules.advertisement.entities import C2CAdvertisement
from packages.business.modules.advertisement.repositories import C2CAdvertisementSqlRepository
from packages.core.service.sql_service import SqlService

class C2CAdvertisementSqlService(SqlService[C2CAdvertisement]):
    def __init__(self, repository: C2CAdvertisementSqlRepository):
        super().__init__(repository)
        self.repository = repository

    def get_changed_ads_count(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime
    ):
        return self.repository.get_changed_ads_count(start_date, end_date)

    def get_changed_ads(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            offset: int,
            limit: int
    ):
        return self.repository.get_changed_ads(start_date, end_date, offset, limit)


    def get_ad(
            self,
            id: int
    ):
        return self.repository.get_by_id(id)

    def get_ads_by_category_ids(
            self,
            category_ids: List[int],
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[C2CAdvertisement]:
        """
        Get advertisements filtered by category IDs with optional limit and offset.
        
        Args:
            category_ids: List of category IDs to filter by
            limit: Maximum number of results to return (optional)
            offset: Number of results to skip (optional)
        
        Returns:
            List of C2CAdvertisement entities matching the category IDs
        """
        return self.repository.get_ads_by_category_ids(category_ids, limit=limit, offset=offset)



