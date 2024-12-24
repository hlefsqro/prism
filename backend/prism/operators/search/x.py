from typing import Optional, List

import aiohttp
from langchain_core.documents import Document
from pydantic import BaseModel

from prism.common.config import SETTINGS
from prism.operators.search import SearchOp


class XSearchReq(BaseModel):
    query: str
    max_results: int = 10


class XSearchOp(SearchOp):

    async def search(self, input: XSearchReq) -> Optional[List[Document]]:
        headers = {
            'Authorization': f'Bearer {SETTINGS.X_BEARER_TOKEN}'
        }

        search_url = "https://api.twitter.com/2/tweets/search/recent"
        query_params = {
            'query': input.query,
            'max_results': input.max_results,
            'tweet.fields': 'created_at,public_metrics',
        }

        # query_params = {
        #     'query': input.query,
        #     'max_results': input.max_results,
        #     'expansions': 'attachments.media_keys',
        #     'tweet.fields': 'created_at',
        #     'media.fields': 'url,type,preview_image_url'
        # }

        ret = []

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers, params=query_params) as response:
                response.raise_for_status()
                tweets = await response.json()

                if tweets.get('data', None):
                    for tweet in tweets['data']:
                        metadata = {
                            "created_at": tweet.get("created_at", ""),
                            "query": input.query,
                            "site": "x"
                        }
                        doc = Document(
                            page_content=tweet["text"],
                            metadata=metadata,
                        )
                        ret.append(doc)

        return ret
