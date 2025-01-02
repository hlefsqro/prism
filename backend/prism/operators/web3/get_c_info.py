from typing import Optional, Dict

from pydantic import BaseModel

from prism.common.config import SETTINGS
from prism.operators.web3 import CmcOp


class GetCryptoInfoReq(BaseModel):
    symbol_or_address: Optional[str] = None
    symbol: Optional[str] = None
    address: Optional[str] = None


class CryptoInfo(BaseModel):
    status: Optional[Dict] = None
    data: Optional[Dict] = None


class GetCryptoInfo(CmcOp):
    url: str = f"{SETTINGS.C_PRO_BASE_URL}/v2/cryptocurrency/info"

    async def call(self, input: GetCryptoInfoReq = None) -> Optional[CryptoInfo]:
        if input and not input.symbol_or_address:
            return await super().call(input)
        ret = await super().call(GetCryptoInfoReq(address=input.symbol_or_address))
        if ret:
            return ret
        return await super().call(GetCryptoInfoReq(symbol=input.symbol_or_address))

    async def _to_resp(self, json: dict) -> Optional[CryptoInfo]:
        ret = None
        if json and isinstance(json.get("data", None), dict):
            ret = CryptoInfo(**json)
        return ret
