from datetime import datetime

from sqlalchemy import text

from packages.business.modules.advertisement.entities import Advertisement
from packages.business.modules.advertisement.services import AdvertisementSqlService
from packages.core.registry import Registry
from packages.core.scheduler.task import Task
from packages.core.sql_connector import SqlConnector


class AdvertisementBatchUpdate:
    def __init__(
            self,
            offset: int,
            limit: int,
            start: datetime,
            end: datetime
    ):
        self.offset = offset
        self.limit = limit
        self.start = start
        self.end = end

    def get_changed_ads(self):
        connector = Registry().get(SqlConnector, salt='source')
        session = connector.get_session()
        result = session.execute(
            text(
                f"""
                SELECT 
                    id,
                    title_fa,
                    description_fa,
                    status,
                    product_id,
                    changed_at,
                    created_at 
                FROM c2c_advertisements 
                WHERE changed_at >= :start AND changed_at <= :end LIMIT :limit OFFSET :offset
                """
            ),
            {
                'start': self.start,
                'end': self.end,
                'limit': self.limit,
                'offset': self.offset
            }
        ).fetchall()
        session.close()
        return result

    def execute(self):
        print(f"Updating ads from {self.start} to {self.end} with offset {self.offset} and limit {self.limit}")
        changed_ads = self.get_changed_ads()
        print(f"Found {len(changed_ads)} ads to update")
        for ad in changed_ads:
            print(f"Updating ad {ad.id}")
            ad_sql_service = Registry().get(AdvertisementSqlService)
            ad_sql_service.update(
                Advertisement(
                    id=ad.id,
                    title=ad.title_fa,
                    description=ad.description_fa,
                    status=ad.status,
                    product_id=ad.product_id,
                    created_at=ad.created_at,
                    changed_at=ad.changed_at
                )
            )


class AdvertisementBatchUpdateTask(Task):

    def __init__(
            self,
            *args,
            **kwargs
    ):
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def get_name(self) -> str:
        return 'advertisement_batch_update'

    def get_args(self):
        return self.args

    def get_kwargs(self):
        return self.kwargs

    def run(
            self,
            *args,
            **kwargs
    ):
        offset = kwargs.get('offset')
        limit = kwargs.get('limit')
        start = kwargs.get('start')
        end = kwargs.get('end')
        batch_update = AdvertisementBatchUpdate(
            offset=offset,
            limit=limit,
            start=start,
            end=end
        )
        batch_update.execute()
