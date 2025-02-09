from typing import TypeVar, Generic
from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from packages.core.entity import Entity

T = TypeVar('T')




class SqlEntity(Entity, DeclarativeBase):


    id : Mapped[int] = mapped_column(Integer, primary_key=True, auto_increment=True)
    created_at : Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at : Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'


