from typing import TypeVar

from packages.core.entity import RedisEntity
from packages.core.service import Service


T = TypeVar('T', bound=RedisEntity)
class RedisService(Service[T]):
    pass