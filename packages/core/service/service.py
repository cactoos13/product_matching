from typing import Generic, TypeVar
from packages.core.repository import SqlRepository
T = TypeVar('T', bound=SqlRepository)

class Service(Generic[T]):
    def __init__(self, repository: T):
        self.repository = repository

    def get_repository(self)-> T:
        return self.repository





