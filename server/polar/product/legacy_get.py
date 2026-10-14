from polar.exceptions import ResourceNotFound
from polar.models import Product
from polar.postgres import AsyncReadSession

from . import auth
from .schemas import ProductID
from .service import product as product_service


async def get(
    id: ProductID,
    auth_subject: auth.CreatorProductsRead,
    session: AsyncReadSession,
) -> Product:
    """Get a product by ID."""
    product = await product_service.get(session, auth_subject, id)

    if product is None:
        raise ResourceNotFound()

    return product
