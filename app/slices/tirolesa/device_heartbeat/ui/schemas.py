from datetime import datetime

from pydantic import BaseModel


class HeartbeatResponse(BaseModel):
    server_time: datetime
