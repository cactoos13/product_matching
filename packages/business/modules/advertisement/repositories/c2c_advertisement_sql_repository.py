from datetime import datetime
from typing import Type, List, Optional

from packages.business.modules.advertisement.entities import Advertisement
from packages.core.repository import SqlRepository
from packages.core.sql_connector import SqlConnector


class C2CAdvertisementSqlRepository(SqlRepository[Advertisement]):

    def __init__(self, entity: Type[Advertisement], sql_connector: SqlConnector):
        super().__init__(entity, sql_connector)

    @classmethod
    def get_connector_salt(cls) -> str | None:
        return "source"

    def get_changed_ads_count(
            self,
            start_date: datetime,
            end_date: datetime
    ) -> int:
        return (
            self.get_session()
            .query(self.entity)
            .filter(self.entity.changed_at >= start_date, self.entity.changed_at <= end_date)
            .count()
        )

    def get_changed_ads(
            self,
            start_date: datetime,
            end_date: datetime,
            offset: int,
            limit: int
    ) -> List[Type[Advertisement]]:
        return (
            self.get_session()
            .query(self.entity)
            .filter(self.entity.changed_at >= start_date, self.entity.changed_at <= end_date)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_ads_by_category_ids(
            self,
            category_ids: List[int],
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[Type[Advertisement]]:
        """
        Get advertisements filtered by category IDs with optional limit and offset.
        
        Args:
            category_ids: List of category IDs to filter by
            limit: Maximum number of results to return (optional)
            offset: Number of results to skip (optional)
        
        Returns:
            List of Advertisement entities matching the category IDs
        """
        query = (
            self.get_session()
            .query(self.entity)
            .filter(self.entity.category_id.in_(category_ids))
        )
        
        if offset is not None:
            query = query.offset(offset)
        
        if limit is not None:
            query = query.limit(limit)
        
        return query.all()



