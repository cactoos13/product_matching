from bootstrap import bootstrap
from packages.business.modules.advertisement import AdvertisementModule
from packages.core.registry import Registry
from packages.core.scheduler import Scheduler

modules = [
    AdvertisementModule
]
bootstrap(total=True, modules=modules)

scheduler = Registry().get(Scheduler)
scheduler = scheduler.get_app()
