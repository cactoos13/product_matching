from packages.business.modules.advertisement.entities import Advertisement
from packages.core.repository import SqlRepository


class AdvertisementSqlRepository(SqlRepository[Advertisement]):
    pass
