from typing import Optional

from pydantic import BaseModel

from prism.operators.cmc.get_cmc_info import GetCryptoInfoReq, GetCryptoInfo


class CmcCrypto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    urls: Optional[dict] = None
    platform: Optional[dict] = None


CMC_MAPPING: dict[str, dict] = {}


async def get_crypto_mapping(key: str) -> Optional[CmcCrypto]:
    m = CMC_MAPPING.get(key, None)
    if m:
        return m
    ret = await GetCryptoInfo().call(GetCryptoInfoReq(symbol_or_address=key))
    if ret.data:
        for d in ret.data.values():
            if isinstance(d, dict):
                CMC_MAPPING[key] = CmcCrypto(**d)
            if isinstance(d, list):
                for item in d:
                    if isinstance(item, dict):
                        if item.get("category") == 'coin':
                            CMC_MAPPING[key] = CmcCrypto(**item)
                        elif item.get("category") == 'token':
                            contract_address = item.get('contract_address', [])
                            if contract_address and len(contract_address) > 0:
                                ca = contract_address[0].get('contract_address', None)
                                if ca:
                                    CMC_MAPPING[ca] = CmcCrypto(**item)
    return CMC_MAPPING.get(key, None)
