from packages.business.core.module import BusinessModule
from packages.business.modules.product.entities.product_entity import Product

ProductModule = (
    BusinessModule(
        'product'
    ).add_entity(Product)
    .add_repository(ProductSqlRepository)
)