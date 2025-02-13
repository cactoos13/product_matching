
from packages.business.modules.system_task.entities import SystemTask, SystemTaskTypeEnum, \
    SystemTaskStatusEnum
from packages.core.repository import SqlRepository


class SystemTaskSqlRepository(SqlRepository[SystemTask]):

    def get_last_sync(self) -> SystemTask | None:
        return (
            self.get_session()
            .query(SystemTask)
            .filter(
                SystemTask.type == SystemTaskTypeEnum.SYNCHRONIZE_ADS,
                SystemTask.status == SystemTaskStatusEnum.DONE,

            ).order_by(SystemTask.done_at.desc()).first())

    def get_last_idx(self) -> SystemTask | None:
        return (
            self.get_session()
            .query(SystemTask)
            .filter(
                SystemTask.type == SystemTaskTypeEnum.INDEX_ADVERTISEMENTS,
                SystemTask.status == SystemTaskStatusEnum.DONE
            ).order_by(SystemTask.created_at.desc()).first()
        )
