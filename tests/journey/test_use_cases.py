import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime
from app.slices.journey.register_journey.application.use_case import RegisterJourney
from app.slices.journey.list_my_journeys.application.use_case import ListMyJourneys
from app.slices.journey.update_journey.application.use_case import UpdateJourney, JourneyNotFoundError
from app.slices.journey.delete_journey.application.use_case import DeleteJourney

@pytest.mark.asyncio
async def test_register_journey_use_case():
    repo = AsyncMock()
    use_case = RegisterJourney(repo)
    user_id = uuid4()
    lat, lng = -3.7, -38.5
    
    await use_case.execute(user_id, lat, lng)
    
    repo.create.assert_called_once_with(user_id=user_id, latitude=lat, longitude=lng)

@pytest.mark.asyncio
async def test_list_my_journeys_use_case():
    repo = AsyncMock()
    use_case = ListMyJourneys(repo)
    user_id = uuid4()
    
    await use_case.execute(user_id)
    
    repo.list_by_user.assert_called_once_with(user_id)

@pytest.mark.asyncio
async def test_update_journey_use_case_success():
    repo = AsyncMock()
    journey = MagicMock()
    journey.original_data = None
    journey.latitude = 1.0
    journey.longitude = 2.0
    journey.timestamp = datetime.now()
    
    repo.get_by_id.return_value = journey
    use_case = UpdateJourney(repo)
    
    journey_id = uuid4()
    await use_case.execute(journey_id, 3.0, 4.0, None, "reason")
    
    repo.update.assert_called_once()
    # Check if original data was captured
    args, kwargs = repo.update.call_args
    assert kwargs['original_data']['latitude'] == 1.0

@pytest.mark.asyncio
async def test_update_journey_use_case_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    use_case = UpdateJourney(repo)
    
    with pytest.raises(JourneyNotFoundError):
        await use_case.execute(uuid4(), 3.0, 4.0, None, "reason")

@pytest.mark.asyncio
async def test_delete_journey_use_case():
    repo = AsyncMock()
    journey = MagicMock()
    repo.get_by_id.return_value = journey
    use_case = DeleteJourney(repo)
    
    journey_id = uuid4()
    await use_case.execute(journey_id)
    
    repo.soft_delete.assert_called_once_with(journey)
