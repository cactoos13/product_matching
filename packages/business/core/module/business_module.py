from packages.core.module import Module
from packages.core.registry.registry import Registry
from packages.core.repository import SqlRepository
from packages.core.scheduler import Scheduler
from packages.core.sql_connector import SqlConnector


class BusinessModule(Module):

    def install(self):
        if len(self.entities) == len(self.services) == len(self.repositories):
            self.install_entities(self.entities)
            self.install_repositories(self.repositories)
            self.install_services(self.services)
            self.install_periodic_tasks(self.periodic_tasks)
        else:
            raise ValueError('The number of entities, services and repositories must be equal')

    def install_entities(self, entities):
        pass

    def install_repositories(self, repositories):
        sql_connector = Registry().get(SqlConnector)
        for idx, repository in enumerate(repositories):
            if issubclass(repository, SqlRepository):
                Registry().register(
                    repository,
                    repository[self.entities[idx]](self.entities[idx], sql_connector)
                )

    def install_services(self, services):
        for idx, service in enumerate(services):
            Registry().register(
                service,
                service[self.repositories[idx]](Registry().get(self.repositories[idx]))
            )

    def install_periodic_tasks(self, periodic_tasks):
        for periodic_task in periodic_tasks:
            (Registry().get(Scheduler).register_periodic_task(periodic_task))


