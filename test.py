from typing import TypeVar, Type, Self


class A:
    pass

class B:
    pass



T = TypeVar('T')
class Registry:
    def __init__(self):
        self.registry = {}

    def register(self, key: Type[T], value: T)-> Self:
        self.registry[key] = value
        return Self

    def get(self, key: Type[T])-> T:
        return self.registry[key]


registry = Registry()
registry.register(A, A())
registry.register(B, B())

print(registry.get(A))
print(registry.get(B))
