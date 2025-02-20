from ..models import BunnyOperationLog
from ..schemas import PaginationParams, PaginationSchema
from ..utils import paginate


class LogsService:
    @staticmethod
    async def list(params: PaginationParams) -> PaginationSchema:
        return await paginate(BunnyOperationLog, params.page, params.limit)
