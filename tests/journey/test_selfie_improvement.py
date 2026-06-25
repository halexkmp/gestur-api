import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from io import BytesIO
from PIL import Image
from app.slices.journey.register_journey.application.use_case import RegisterJourney

@pytest.mark.asyncio
async def test_register_journey_with_selfie_optimization():
    repo = AsyncMock()
    repo.count_today_by_user.return_value = 0
    repo.get_last_by_user.return_value = None
    
    blob_service = AsyncMock()
    blob_service.upload_selfie.return_value = "https://blob.url/selfie.jpg"
    
    use_case = RegisterJourney(repo, blob_service)
    
    # Create a large image in memory
    large_img = Image.new('RGB', (1200, 1600), color='red')
    img_byte_arr = BytesIO()
    large_img.save(img_byte_arr, format='JPEG')
    selfie_content = img_byte_arr.getvalue()
    
    user_id = uuid4()
    await use_case.execute(user_id, -3.7, -38.5, selfie_file=selfie_content)
    
    # Verify blob service was called
    blob_service.optimize_image.assert_called_once()
    blob_service.upload_selfie.assert_called_once()
    
    # Since we mocked blob_service, let's also check if optimize_image is functional in the real VercelBlobService
    from app.shared.infra.image_service import ImageService
    real_blob_service = ImageService()
    optimized_content = real_blob_service.optimize_image(selfie_content)
    
    # Verify optimized image properties
    optimized_img = Image.open(BytesIO(optimized_content))
    assert optimized_img.width == 800
    assert optimized_img.format == 'JPEG'
    
    # Verify repo.create was called with the selfie_id from blob service
    repo.create.assert_called_once_with(
        user_id=user_id,
        latitude=-3.7,
        longitude=-38.5,
        selfie_id="https://blob.url/selfie.jpg"
    )

@pytest.mark.asyncio
async def test_register_journey_without_selfie():
    repo = AsyncMock()
    repo.count_today_by_user.return_value = 0
    repo.get_last_by_user.return_value = None
    
    use_case = RegisterJourney(repo)
    
    user_id = uuid4()
    await use_case.execute(user_id, -3.7, -38.5)
    
    repo.create.assert_called_once_with(
        user_id=user_id,
        latitude=-3.7,
        longitude=-38.5,
        selfie_id=None
    )
