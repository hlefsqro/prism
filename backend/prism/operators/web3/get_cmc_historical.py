from typing import Optional

from pydantic import BaseModel

from prism.operators.web3 import CmcOp


class GetCryptoHistoricalReq(BaseModel):
    id: Optional[str] = None
    convert: str = "USD"
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    count: int = 20


class GetCryptoHistorical(CmcOp):
    url: str = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/historical"

    async def _to_resp(self, json: dict) -> Optional[dict]:
        return json
