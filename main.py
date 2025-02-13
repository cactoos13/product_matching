from fastapi import FastAPI
from pydantic import BaseModel

from bootstrap import bootstrap
from packages.business.modules.advertisement.services.advertisement_redis_service import AdvertisementRedisService
from packages.core.registry import Registry
from packages.core.scheduler import Scheduler
from modules import Modules


bootstrap(total=True, modules=Modules)


scheduler = Registry().get(Scheduler)
scheduler = scheduler.get_app()



app = FastAPI()
class TextInput(BaseModel):
    text: str
@app.get("/find")
async def find(input_data: TextInput):
    return Registry().get(AdvertisementRedisService).query(input_data.text)





