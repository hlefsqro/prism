from typing import Optional, List

from pydantic import BaseModel

from prism.operators.web3 import CmcOp


class GetCmcMapReq(BaseModel):
    start: int
    limit: int = 1000


class CmcMap(BaseModel):
    id: int
    name: str
    symbol: str

    rank: Optional[int] = None
    slug: Optional[str] = None
    is_active: Optional[bool] = None
    platform: Optional[str] = None


class GetCmcMap(CmcOp):
    url: str = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"

    async def _to_resp(self, json: dict) -> List[CmcMap]:
        ret = []
        if json and isinstance(json.get("data", None), list):
            maps = json.get("data", [])
            for m in maps:
                ret.append()

        return ret
