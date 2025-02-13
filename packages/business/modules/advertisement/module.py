from packages.business.core.module import BusinessModule
from packages.business.modules.advertisement.entities import Advertisement, AdvertisementIdx
from packages.business.modules.advertisement.repositories import AdvertisementRedisRepository
from packages.business.modules.advertisement.repositories.advertisement_sql_repository import AdvertisementSqlRepository
from packages.business.modules.advertisement.services.advertisement_redis_service import AdvertisementRedisService
from packages.business.modules.advertisement.services.advertisement_sql_service import AdvertisementSqlService
from packages.business.modules.advertisement.tasks.once.advertisement_batch_update_task import \
    AdvertisementBatchUpdateTask
from packages.business.modules.advertisement.tasks.periodic import AdvertisementIndexerTask
from packages.business.modules.advertisement.tasks.periodic.advertisement_synchronizer_task import AdvertisementSynchronizerTask

AdvertisementModule = (
    BusinessModule(
        'advertisement',
    )
    .add_entity(Advertisement)
    .add_repository(AdvertisementSqlRepository)
    .add_service(AdvertisementSqlService)
    .add_entity(AdvertisementIdx)
    .add_repository(AdvertisementRedisRepository)
    .add_service(AdvertisementRedisService)
    .add_task(AdvertisementBatchUpdateTask)
    .add_periodic_task(AdvertisementSynchronizerTask)
    .add_periodic_task(AdvertisementIndexerTask)
)
