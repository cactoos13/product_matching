import enum
from sqlalchemy import String, Enum, Integer
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


    status: Mapped[AdvertisementStatusEnum] = mapped_column(Enum(AdvertisementStatusEnum), nullable=False, default= AdvertisementStatusEnum.PENDING, index=True)
    title: Mapped[String] = mapped_column(String(1000), nullable=False)
    description: Mapped[String] = mapped_column(String(4000), nullable=False)
    product_id: Mapped[Integer] = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

