from app.shared.db.models import LatenessConfiguration


class GetLatenessConfigurationRepository:
    async def get(self) -> LatenessConfiguration | None:
        return await LatenessConfiguration.all().order_by("created_at").first()
