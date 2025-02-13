from typing import TypeVar, Generic

T = TypeVar('T')


class A(Generic[T]):
    def __init__(self, entity: T):
        self.entity = entity

    def get_entity(self) -> T:
        return self.entity


class B(A[T]):
    def __init__(self, entity: T):
        super().__init__(entity)



B[int](1)