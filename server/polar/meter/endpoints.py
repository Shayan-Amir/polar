from zoneinfo import ZoneInfo

from fastapi import Depends, Query
from pydantic import AwareDatetime
from pydantic_extra_types.timezone_name import TimeZoneName

from polar.customer.schemas.customer import CustomerID
from polar.exceptions import PolarRequestValidationError, ResourceNotFound
from polar.kit.metadata import MetadataQuery, get_metadata_query_openapi_schema
from polar.kit.pagination import ListResource, PaginationParamsQuery
from polar.kit.schemas import MultipleQueryFilter
from polar.kit.time_queries import MIN_DATETIME, TimeInterval, is_under_limits
from polar.meter.aggregation import AggregationFunction
from polar.models import Meter
from polar.openapi import APITag
from polar.organization.schemas import OrganizationID
from polar.postgres import (
    AsyncReadSession,
    AsyncSession,
    get_db_read_session,
    get_db_session,
)
from polar.routing import APIRouter

from . import auth, sorting
from .schemas import Meter as MeterSchema
from .schemas import MeterCreate, MeterID, MeterQuantities, MeterUpdate
from .service import meter as meter_service

router = APIRouter(
    prefix="/meters", tags=["meters", APITag.public, APITag.mcp, APITag.cli]
)


MeterNotFound = {
    "description": "Meter not found.",
    "model": ResourceNotFound.schema(),
}


@router.get(
    "/",
    summary="List Meters",
    response_model=ListResource[MeterSchema],
    openapi_extra={"parameters": [get_metadata_query_openapi_schema()]},
)
async def list(
    auth_subject: auth.MeterRead,
    pagination: PaginationParamsQuery,
    sorting: sorting.ListSorting,
    metadata: MetadataQuery,
    organization_id: MultipleQueryFilter[OrganizationID] | None = Query(
        None, title="OrganizationID Filter", description="Filter by organization ID."
    ),
    query: str | None = Query(None, description="Filter by name."),
    is_archived: bool | None = Query(None, description="Filter on archived meters."),
    session: AsyncReadSession = Depends(get_db_read_session),
) -> ListResource[MeterSchema]:
    """List meters."""
    results, count = await meter_service.list(
        session,
        auth_subject,
        organization_id=organization_id,
        metadata=metadata,
        query=query,
        is_archived=is_archived,
        pagination=pagination,
        sorting=sorting,
    )

    return ListResource.from_paginated_results(
        [MeterSchema.model_validate(result) for result in results],
        count,
        pagination,
    )


@router.get(
    "/{id}",
    summary="Get Meter",
    response_model=MeterSchema,
    responses={404: MeterNotFound},
)
async def get(
    id: MeterID,
    auth_subject: auth.MeterRead,
    session: AsyncReadSession = Depends(get_db_read_session),
) -> Meter:
    """Get a meter by ID."""
    meter = await meter_service.get(session, auth_subject, id)

    if meter is None:
        raise ResourceNotFound()

    return meter



@router.post(
    "/",
    response_model=MeterSchema,
    status_code=201,
    summary="Create Meter",
    responses={201: {"description": "Meter created."}},
)
async def create(
    meter_create: MeterCreate,
    auth_subject: auth.MeterWrite,
    session: AsyncSession = Depends(get_db_session),
) -> Meter:
    """Create a meter."""
    return await meter_service.create(session, meter_create, auth_subject)


@router.patch(
    "/{id}",
    response_model=MeterSchema,
    summary="Update Meter",
    responses={
        200: {"description": "Meter updated."},
        404: MeterNotFound,
    },
)
async def update(
    id: MeterID,
    meter_update: MeterUpdate,
    auth_subject: auth.MeterWrite,
    session: AsyncSession = Depends(get_db_session),
) -> Meter:
    """Update a meter."""
    meter = await meter_service.get(session, auth_subject, id)

    if meter is None:
        raise ResourceNotFound()

    return await meter_service.update(session, meter, meter_update, auth_subject)
