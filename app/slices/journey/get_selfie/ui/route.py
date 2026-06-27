from fastapi import APIRouter, HTTPException, Response, Query
from app.slices.journey.get_selfie.application.use_case import GetSelfie, SelfieNotFoundError

router = APIRouter()
use_case = GetSelfie()

@router.get("")
async def route(selfie_id: str = Query(..., description="The full URL of the selfie image")):
    try:
        content = await use_case.execute(selfie_url=selfie_id)
        return Response(content=content, media_type="image/jpeg")
    except SelfieNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error while retrieving selfie")
