from fastapi import APIRouter, Depends, Response, status

from app.shared.security.device_auth import get_current_device
from app.slices.tirolesa.record_trip.application.use_case import RecordTrip
from app.slices.tirolesa.record_trip.infra.repository import RecordTripRepository
from .schemas import RecordTripRequest, RecordTripResponse

router = APIRouter()

use_case = RecordTrip(RecordTripRepository())


@router.post("/trips", response_model=RecordTripResponse, status_code=status.HTTP_201_CREATED)
async def route(data: RecordTripRequest, response: Response, device=Depends(get_current_device)):
    created = await use_case.execute(
        device_id=device.id,
        trip_id=data.id,
        start=data.start,
        end=data.end,
        passengers=data.passengers,
    )
    if not created:
        response.status_code = status.HTTP_200_OK
    return RecordTripResponse(id=data.id, duplicate=not created)
