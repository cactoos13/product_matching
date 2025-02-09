from packages.business.core.module import BusinessModule
from packages.business.modules.advertisement.entities import Advertisement
from packages.business.modules.advertisement.repositories.advertisement_sql_repository import AdvertisementSqlRepository
from packages.business.modules.advertisement.services.advertisement_sql_service import AdvertisementSqlService
from packages.core.registry.registry import Registry
from packages.core.sql_connector.sql_connector import SqlConnector

AdvertisementModule = (
    BusinessModule(
        'advertisement',
        Registry().get(SqlConnector),
    )
    .add_entity(Advertisement)
    .add_repository(AdvertisementSqlRepository[Advertisement])
    .add_service(AdvertisementSqlService[AdvertisementSqlRepository])
)
