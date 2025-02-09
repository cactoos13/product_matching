from typing import Generic, TypeVar

from sqlalchemy.orm import Session
from packages.core.entity import SqlEntity
from packages.core.repository import Repository
from packages.core.sql_connector.sql_connector import SqlConnector

T = TypeVar('T', bound=SqlEntity)
class SqlRepository(Generic[T], Repository):
    def __init__(
            self,
            entity: T,
            sql_connector: SqlConnector | None = None
    ):
        self.sql_connector = sql_connector
        self.entity = entity

    def get_entity(self)-> T:
        return self.entity

    def get_session(self)-> Session:
        return self.sql_connector.get_session()

    def save(self, entity: T):
        session = self.get_session()
        session.add(entity)
        session.commit()
        session.close()

    def get_all(self)-> [T]:
        session = self.get_session()
        result = session.query(self.entity.__class__).all()
        session.close()
        return result

    def get_by_id(self, id: int)-> T:
        session = self.get_session()
        result = session.query(self.entity.__class__).filter(self.entity.__class__.id == id).first()
        session.close()
        return result

    def delete(self, entity: T):
        session = self.get_session()
        session.delete(entity)
        session.commit()
        session.close()

    def update(self, entity: T):
        session = self.get_session()
        session.merge(entity)
        session.commit()
        session.close()

    def get_by(self, **kwargs)-> [T]:
        session = self.get_session()
        result = session.query(self.entity.__class__).filter_by(**kwargs).all()
        session.close()
        return result















