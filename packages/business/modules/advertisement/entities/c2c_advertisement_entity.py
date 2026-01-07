import enum
from datetime import datetime

from sqlalchemy import String, Enum, Integer, DateTime, Boolean, TypeDecorator
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


class CaseInsensitiveEnum(TypeDecorator):
    """Custom type that converts uppercase enum values to lowercase for compatibility with source database"""
    impl = String
    cache_ok = True
    
    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        return str(value).lower()
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # Convert uppercase to lowercase to match enum values
        value_lower = str(value).lower()
        try:
            return self.enum_class(value_lower)
        except ValueError:
            # If value doesn't match, try to find by name (for backwards compatibility)
            try:
                return self.enum_class[value.upper()]
            except (KeyError, AttributeError):
                raise ValueError(f"Invalid enum value: {value}")

class C2CAdvertisement(SqlEntity):
    __tablename__ = 'c2c_advertisements'
    __mapper_args__ = {
        'exclude_properties': ['updated_at']
    }

    status: Mapped[AdvertisementStatusEnum] = mapped_column(CaseInsensitiveEnum(AdvertisementStatusEnum, length=50), nullable=False, default=AdvertisementStatusEnum.PENDING, index=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False, name='title_fa')
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True, name='description_fa')
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # lsh_indexed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)


    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

