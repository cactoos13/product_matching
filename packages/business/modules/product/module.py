from packages.business.core.module import BusinessModule
from packages.business.modules.product.entities import Product
from packages.business.modules.product.repositories import ProductSqlRepository
from packages.business.modules.product.services import ProductSqlService

ProductModule = (
    BusinessModule(
        'product'
    ).add_entity(Product)
    .add_repository(ProductSqlRepository)
    .add_service(ProductSqlService)

)