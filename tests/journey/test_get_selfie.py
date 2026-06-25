import pytest
from unittest.mock import AsyncMock
from app.slices.journey.get_selfie.application.use_case import GetSelfie, SelfieNotFoundError

@pytest.mark.asyncio
async def test_get_selfie_success():
    image_service = AsyncMock()
    image_service.download_selfie.return_value = b"fake-image-content"
    
    use_case = GetSelfie(image_service)
    selfie_url = "https://blob.url/images/selfie.jpg"
    
    content = await use_case.execute(selfie_url)
    
    assert content == b"fake-image-content"
    image_service.download_selfie.assert_called_once_with(selfie_url)

@pytest.mark.asyncio
async def test_get_selfie_not_found():
    image_service = AsyncMock()
    image_service.download_selfie.return_value = b""
    
    use_case = GetSelfie(image_service)
    selfie_url = "https://blob.url/images/notfound.jpg"
    
    with pytest.raises(SelfieNotFoundError):
        await use_case.execute(selfie_url)
    
    image_service.download_selfie.assert_called_once_with(selfie_url)

@pytest.mark.asyncio
async def test_get_selfie_none():
    image_service = AsyncMock()
    image_service.download_selfie.return_value = None
    
    use_case = GetSelfie(image_service)
    selfie_url = "https://blob.url/images/none.jpg"
    
    with pytest.raises(SelfieNotFoundError):
        await use_case.execute(selfie_url)
    
    image_service.download_selfie.assert_called_once_with(selfie_url)
