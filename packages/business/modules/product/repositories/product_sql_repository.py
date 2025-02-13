
from packages.business.modules.product.entities import Product
from packages.core.repository import SqlRepository


class ProductSqlRepository(SqlRepository[Product]):
    pass