import aiohttp
from pydantic import BaseModel

from prism.common.config import SETTINGS
from prism.operators.search import SearchOp


class XCountReq(BaseModel):
    query: str
    start_time: str
    end_time: str


class XCountOp(SearchOp):

    async def search(self, input: XCountReq) -> int:
        headers = {
            'Authorization': f'Bearer {SETTINGS.X_BEARER_TOKEN}'
        }

        search_url = "https://api.twitter.com/2/tweets/search/recent"
        query_params = {
            'start_time': input.start_time,
            'end_time': input.end_time,
            'query': input.query,
            'max_results': 100,
        }

        ret = 0

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers, params=query_params) as response:
                response.raise_for_status()
                json = await response.json()
                if json.get('data', None):
                    ret = len(json['data'])

        return ret
