from datetime import datetime

from packages.business.modules.system_task.entities import SystemTask, SystemTaskStatusEnum
from packages.business.modules.system_task.repositories import SystemTaskSqlRepository
from packages.core.service.sql_service import SqlService


class SystemTaskSqlService(SqlService[SystemTask]):

    def __init__(self, repository: SystemTaskSqlRepository):
        super().__init__(repository)
        self.repository = repository

    def get_repository(self) -> SystemTaskSqlRepository:
        return self.repository

    def get_last_sync(self)-> SystemTask | None:
        return self.repository.get_last_sync()

    def get_last_idx(self) -> SystemTask | None:
        return self.repository.get_last_idx()


    def save(self, entity: SystemTask):
        return self.repository.save(entity)


    def done_the_task(self, task: SystemTask):
        task.status = SystemTaskStatusEnum.DONE
        task.done_at = datetime.now()
        self.repository.update(task)

    def fail_the_task(self, task: SystemTask):
        task.status = SystemTaskStatusEnum.FAILED
        task.done_at = datetime.now()
        self.repository.update(task)


