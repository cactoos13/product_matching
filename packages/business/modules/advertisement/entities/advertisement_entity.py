import enum
from datetime import datetime

from sqlalchemy import String, Enum, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.core.entity.sql_entity import SqlEntity


class AdvertisementStatusEnum(enum.Enum):
    DRAFT = 'draft'
    PENDING = 'pending'
    PENDING_AFTER_APPROVE = 'pending_after_approve'
    REJECTED = 'rejected'
    APPROVED = 'approved'
    USER_REPORTED = 'user_reported'
    USER_DELETED = 'user_deleted'
    EXPIRED = 'expired'
    RESERVED = 'reserved'
    SOLD = 'sold'
    DEPRECATED = 'deprecated'

class Advertisement(SqlEntity):
    __tablename__ = 'advertisement'

    status: Mapped[AdvertisementStatusEnum] = mapped_column(Enum(AdvertisementStatusEnum), nullable=False, default= AdvertisementStatusEnum.PENDING, index=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    lsh_indexed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)


    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

