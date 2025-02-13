import datetime
from typing import Type

from packages.business.modules.advertisement.entities import Advertisement
from packages.business.modules.advertisement.repositories import AdvertisementSqlRepository
from packages.core.service.sql_service import SqlService

class AdvertisementSqlService(SqlService[Advertisement]):
    def __init__(self, repository: AdvertisementSqlRepository):
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
            page: int,
            offset: int
    ):
        return self.repository.get_changed_ads(start_date, end_date, page, offset)

    def get_not_lsh_indexed_ads_count(self) -> int:
        return self.repository.get_not_lsh_indexed_ads_count()

    def get_not_lsh_indexed_ads(
            self,
            limit: int,
            offset: int
    ) -> list[Type[Advertisement]]:
        return self.repository.get_not_lsh_indexed_ads(limit, offset)


    def index_ads(self, ads: [Advertisement]):
        return self.repository.index_ads_batch(ads)

