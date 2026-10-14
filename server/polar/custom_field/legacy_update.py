from polar.exceptions import ResourceNotFound
from polar.models import CustomField
from polar.postgres import AsyncSession

from . import auth
from .endpoints import CustomFieldID
from .schemas import CustomFieldUpdate
from .service import custom_field as custom_field_service


async def update(
    id: CustomFieldID,
    custom_field_update: CustomFieldUpdate,
    auth_subject: auth.CustomFieldWrite,
    session: AsyncSession,
) -> CustomField:
    """Update a custom field."""
    custom_field = await custom_field_service.get_by_id(session, auth_subject, id)

    if custom_field is None:
        raise ResourceNotFound()

    return await custom_field_service.update(
        session, custom_field, custom_field_update, auth_subject
    )
