import enum
from sqlalchemy import Enum, String, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from packages.core.entity import SqlEntity


class ProductStatusEnum(enum.Enum):
    MARKETABLE = 'marketable'
    COMING_SOON = 'coming_soon'
    STOP_PRODUCTION = 'stop_production'

class ProductModerationStatusEnum(enum.Enum):
    MODERATION_STATUS_DRAFT = 'draft'
    MODERATION_STATUS_IN_REVIEW = 'in_review'
    MODERATION_STATUS_WAITING_FOR_CONFIRM = 'waiting_for_confirm'
    MODERATION_STATUS_WAITING_FOR_PHOTO = 'waiting_for_photo'
    MODERATION_STATUS_EDIT_AFTER_APPROVED = 'edit_after_approved'
    MODERATION_STATUS_APPROVED = 'approved'
    MODERATION_STATUS_REJECTED = 'rejected'
    MODERATION_STATUS_IN_REVIEW_AFTER_APPROVED = 'in_review_after_approved'
    MODERATION_STATUS_REMOVED = 'removed'
    MODERATION_STATUS_DUPLICATE = 'duplicate'

class Product(SqlEntity):
    __tablename__ = 'products'

    status: Mapped[ProductStatusEnum] = mapped_column(Enum(ProductStatusEnum), nullable=False, default= ProductStatusEnum.MARKETABLE, index=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(String(4000), nullable=False)
    moderation_status: Mapped[ProductModerationStatusEnum] = mapped_column(Enum(ProductModerationStatusEnum), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)





