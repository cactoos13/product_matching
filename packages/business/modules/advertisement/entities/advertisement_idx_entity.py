
from packages.core.entity import RedisEntity


class AdvertisementIdx(RedisEntity):
    def __init__(
            self,
            id: int,
            text: str,
    ):
        super().__init__()
        self.id = id
        self.text = text


    def get_id(self)-> int:
        return self.id

    def get_text(self)-> str:
        return self.text

