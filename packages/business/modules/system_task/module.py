from packages.business.core.module import BusinessModule
from packages.business.modules.system_task.entities.system_task_entity import SystemTaskEntity
from packages.business.modules.system_task.repositories.system_task_repository import SystemTaskRepository
from packages.business.modules.system_task.services.system_task_service import SystemTaskService

SystemTaskModule = (
    BusinessModule(
        'system_task'
    )
    .add_entity(SystemTaskEntity)
    .add_repository(SystemTaskRepository)
    .add_service(SystemTaskService)
)