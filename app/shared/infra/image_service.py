from io import BytesIO
from PIL import Image
import os
import httpx
from vercel.blob import AsyncBlobClient
from app.config import settings

class ImageService:
    def __init__(self):
        # The SDK reads BLOB_READ_WRITE_TOKEN from environment automatically.
        # We ensure it's set if provided in settings.
        if settings.BLOB_READ_WRITE_TOKEN:
            os.environ["BLOB_READ_WRITE_TOKEN"] = settings.BLOB_READ_WRITE_TOKEN
        self.client = AsyncBlobClient()

    async def upload_selfie(self, file_content: bytes, filename: str) -> str:
        """
        Uploads a selfie to Vercel Blob and returns the URL.
        """
        resp = await self.client.put(
            f"{settings.BLOB_FOLDER}/{filename}",
            body=file_content,
            access="private"
        )
        return resp.url

    async def download_selfie(self, selfie_url: str) -> bytes:
        """
        Downloads a selfie from Vercel Blob using its URL.
        Note: client.get() is available in the SDK to fetch blob content and metadata.
        """
        result = await self.client.get(selfie_url, access="private")
        if result is None or result.status_code != 200:
            return b""
        return result.content
            # Fallback to direct httpx if SDK get fails or for compatibility


    async def delete_selfie(self, selfie_url: str) -> None:
        """
        Deletes a selfie from Vercel Blob.
        """
        await self.client.delete(selfie_url)

    def optimize_image(self, file_content: bytes) -> bytes:
        """
        Optimizes an image by resizing and compressing it.
        """
        img = Image.open(BytesIO(file_content))
        
        # Convert to RGB if necessary (e.g. RGBA)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Resize if width > 800px
        max_width = 800
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
        # Compress
        output = BytesIO()
        img.save(output, format="JPEG", quality=70)
        return output.getvalue()
