from datetime import datetime
from typing import Type, List

from packages.business.modules.advertisement.entities import Advertisement
from packages.core.repository import SqlRepository
from packages.core.sql_connector import SqlConnector


class AdvertisementSqlRepository(SqlRepository[Advertisement]):

    def __init__(self, entity: Type[Advertisement], sql_connector: SqlConnector):
        super().__init__(entity, sql_connector)

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



    def get_not_lsh_indexed_ads_count(self) -> int:
        return (
            self.get_session()
            .query(self.entity)
            .filter(self.entity.lsh_indexed == False)
            .count()
        )

    def get_not_lsh_indexed_ads(
            self,
            limit: int,
            offset: int
    )-> List[Type[Advertisement]]:
        session = self.get_session()
        result = (
            session.query(self.entity)
            .filter(self.entity.lsh_indexed == 0)
            .offset(offset)
            .limit(limit)
            .all()
        )
        session.close()
        return result

    def index_ads_batch(self, ads: List[Advertisement]):
        for ad in ads:
            ad.lsh_indexed = True
        self.save_all(ads)
        return ads
