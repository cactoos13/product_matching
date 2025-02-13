from packages.business.core.module import BusinessModule
from packages.business.modules.system_task.entities.system_task_entity import SystemTask
from packages.business.modules.system_task.repositories.system_task_sql_repository import SystemTaskSqlRepository
from packages.business.modules.system_task.services.system_task_sql_service import SystemTaskSqlService

SystemTaskModule = (
    BusinessModule(
        'system_task'
    )
    .add_entity(SystemTask)
    .add_repository(SystemTaskSqlRepository)
    .add_service(SystemTaskSqlService)
)