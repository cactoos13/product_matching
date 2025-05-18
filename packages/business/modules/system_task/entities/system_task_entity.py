import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from packages.core.entity import SqlEntity

class SystemTaskTypeEnum(enum.Enum):
    INDEX_ADVERTISEMENTS = 'index_advertisements'
    INDEX_ADVERTISEMENTS_WORKER = 'index_advertisements_worker'

    SYNCHRONIZE_PRODUCTS = 'synchronize_products'
    SYNCHRONIZE_PRODUCTS_WORKER = 'synchronize_products_worker'

    SYNCHRONIZE_ADS = 'synchronize_ads'
    SYNCHRONIZE_ADS_WORKER = 'synchronize_ads_worker'

class SystemTaskStatusEnum(enum.Enum):
    PENDING = 'pending'
    DONE = 'done'
    FAILED = 'failed'

class SystemTask(SqlEntity):
    __tablename__ = 'tasks'

    name: Mapped[str] = mapped_column(String(1000), nullable=False)
    type: Mapped[SystemTaskTypeEnum] = mapped_column(Enum(SystemTaskTypeEnum), nullable=False, index=True)
    status: Mapped[SystemTaskStatusEnum] = mapped_column(Enum(SystemTaskStatusEnum), nullable=False, default=SystemTaskStatusEnum.PENDING, index=True)
    done_at: Mapped[datetime | None ] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    parent: Mapped['SystemTask'] = relationship('SystemTask', remote_side='SystemTask.id', backref='children')
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('tasks.id'), nullable=True)

    def __repr__(self):
        return f'<SystemTask {self.id} {self.name} {self.type} {self.status}>'
