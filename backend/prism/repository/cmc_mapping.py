from typing import Optional

from pydantic import BaseModel

from prism.operators.cmc.get_cmc_info import GetCryptoInfoReq, GetCryptoInfo


class CmcCrypto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    urls: Optional[dict] = None
    platform: Optional[dict] = None
    ca: Optional[str] = None


CMC_MAPPING: dict[str, dict] = {}


async def get_crypto_mapping(key: str) -> Optional[CmcCrypto]:
    m = CMC_MAPPING.get(key, None)
    if m:
        return m
    ret = await GetCryptoInfo().call(GetCryptoInfoReq(symbol_or_address=key))
    if ret and ret.data:
        for d in ret.data.values():
            if isinstance(d, dict):
                rrr = CmcCrypto(**d)
                rrr.ca = key
                CMC_MAPPING[key] = rrr
            if isinstance(d, list):
                for item in d:
                    if isinstance(item, dict):
                        if item.get("category") == 'coin':
                            r = CmcCrypto(**item)
                            r.ca = key
                            CMC_MAPPING[key] = r
                        elif item.get("category") == 'token':
                            contract_address = item.get('contract_address', [])
                            if contract_address and len(contract_address) > 0:
                                ca = contract_address[0].get('contract_address', None)
                                if ca:
                                    rr = CmcCrypto(**item)
                                    rr.ca = ca
                                    CMC_MAPPING[ca] = rr
    return CMC_MAPPING.get(key, None)
