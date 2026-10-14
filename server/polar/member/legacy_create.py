from polar.customer.schemas.customer import CustomerID
from polar.postgres import AsyncSession

from . import auth
from .schemas import Member, MemberCreateFromCustomer
from .service import member_service


async def create(
    id: CustomerID,
    member_create: MemberCreateFromCustomer,
    auth_subject: auth.MemberWrite,
    session: AsyncSession,
) -> Member:
    """
    Create a new member for a customer.

    Only B2B customers with the member management feature enabled can add members.
    The authenticated user or organization must have access to the customer's organization.
    """
    created_member = await member_service.create(
        session,
        auth_subject,
        customer_id=id,
        email=member_create.email,
        name=member_create.name,
        external_id=member_create.external_id,
        role=member_create.role,
    )

    return Member.model_validate(created_member)
