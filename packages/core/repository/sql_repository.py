from typing import Type, TypeVar, Generic, List
from sqlalchemy.orm import Session
from packages.core.entity import SqlEntity
from packages.core.repository import Repository
from packages.core.sql_connector.sql_connector import SqlConnector


T = TypeVar('T', bound=SqlEntity)
class SqlRepository(Repository[T]):
    def __init__(self, entity: Type[T], sql_connector: SqlConnector):
        super().__init__(entity)
        self.sql_connector = sql_connector
        self.entity = entity

    def get_entity(self)-> Type[T]:
        return self.entity

    def get_session(self)-> Session:
        return self.sql_connector.get_session()

    def save(self, entity: T)-> T:
        session = self.get_session()
        session.add(entity)
        session.commit()
        session.refresh(entity)
        session.close()
        return entity


    def get_all(self)-> List[T]:
        session = self.get_session()
        result = session.query(self.entity).all()
        session.close()
        return result

    def get_by_id(self, id: int)-> T | None:
        session = self.get_session()
        result = session.query(self.entity).filter(self.entity.id == id).first()
        session.close()
        return result

    def delete(self, entity: T):
        session = self.get_session()
        session.delete(entity)
        session.commit()
        session.close()

    def update(self, entity: T)-> T:
        session = self.get_session()
        res = session.merge(entity)
        session.commit()
        session.close()
        return res

    def get_by(self, **kwargs)-> List[T]:
        session = self.get_session()
        result = session.query(self.entity).filter_by(**kwargs).all()
        session.close()
        return result


    def save_all(self, entities: List[T])-> List[T]:
        session = self.get_session()
        for entity in entities:
            session.add(entity)
        session.commit()
        session.close()
        return entities














