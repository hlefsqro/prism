import logging
from typing import Optional

from pydantic import BaseModel

from prism.common.codec import jsonloads
from prism.operators.web3.get_c_info import GetCryptoInfoReq, GetCryptoInfo

logger = logging.getLogger(__name__)

class CmcCrypto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    urls: Optional[dict] = None
    platform: Optional[dict] = None
    ca: Optional[str] = None


CMC_MAPPING: dict[str, dict] = {}


async def get_crypto_mapping(key: str) -> Optional[CmcCrypto]:
    try:
        m = CMC_MAPPING.get(key, None)
        if m:
            logger.info(f"crypto mapping keys: {list(CMC_MAPPING.keys())}")
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
        logger.info(f"crypto mapping keys: {list(CMC_MAPPING.keys())}")
        return CMC_MAPPING.get(key, None)
    except Exception as e:
        logger.error(f"failed to get crypto mapping: {e}")
        return None
