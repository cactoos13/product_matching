from bootstrap import bootstrap
from packages.core.registry import Registry
from packages.core.scheduler import Scheduler
from modules import Modules


bootstrap(total=True, modules=Modules)
scheduler = Registry().get(Scheduler)
scheduler = scheduler.get_app()


