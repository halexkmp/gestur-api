from app.shared.infra.image_service import ImageService

class SelfieNotFoundError(Exception):
    pass

class GetSelfie:
    def __init__(self, image_service: ImageService = None):
        self.image_service = image_service or ImageService()

    async def execute(self, selfie_url: str) -> bytes:
        """
        Retrieves the selfie image content by its URL (selfie_id).
        """
        content = await self.image_service.download_selfie(selfie_url)
        if not content:
            raise SelfieNotFoundError(f"Selfie with URL {selfie_url} not found or empty.")
        return content
