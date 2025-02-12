from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from packages.core.entity import SqlEntity


class SystemTaskEntity(SqlEntity):
    __tablename__ = 'tasks'

    name: Mapped[str] = mapped_column(String(1000), nullable=False)
    done_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str] = mapped_column(String(1000), nullable=True)
