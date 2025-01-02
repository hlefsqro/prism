from typing import Optional

from pydantic import BaseModel

from prism.operators.web3 import CmcOp


class GetCryptoLatestReq(BaseModel):
    id: Optional[int] = None
    convert: str = "USD"


class GetCryptoLatest(CmcOp):
    url: str = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

    async def _to_resp(self, json: dict) -> Optional[dict]:
        return json
