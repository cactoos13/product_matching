import enum
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from packages.core.entity.sqlentity import SqlEntity


class AdvertisementStatusEnum(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING_AFTER_APPROVED = 'pending_after_approved'
    USER_REPORTED = 'user_reported'
    USER_DELETED = 'user_deleted'
    EXPIRED = 'expired'
    RESERVED = 'reserved'
    SOLD = 'sold'
    DEPRECATED = 'deprecated'
    DRAFT = 'draft'

class Advertisement(SqlEntity):
    __tablename__ = 'advertisement'
    status: Mapped[AdvertisementStatusEnum] = mapped_column(Enum(AdvertisementStatusEnum), nullable=False, default= AdvertisementStatusEnum.PENDING)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(String(4000), nullable=False)


