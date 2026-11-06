from pydantic import BaseModel


class CheckOfflineDevicesResponse(BaseModel):
    marked_offline: int
