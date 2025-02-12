from abc import ABC
from typing import Self, Type

from packages.core.entity import Entity
from packages.core.install import Installable
from packages.core.repository import Repository
from packages.core.scheduler.task import PeriodicTask
from packages.core.service import Service


class Module(Installable, ABC):


    def __init__(self, name: str):
        self.name = name
        self.entities: [Type[Entity]] = []
        self.periodic_tasks : [Type[PeriodicTask]] = []
        self.services: [Type[Service]] = []
        self.repositories: [Type[Repository]] = []

    def add_entity(self, entity: Type[Entity])-> Self:
        self.entities.append(entity)
        return self

    def add_periodic_task(self, periodic_task: Type[PeriodicTask])-> Self:
        self.periodic_tasks.append(periodic_task)
        return self

    def add_service(self, service: Type[Service])-> Self:
        self.services.append(service)
        return self

    def add_repository(self, repository: Type[Repository])-> Self:
        self.repositories.append(repository)
        return self





