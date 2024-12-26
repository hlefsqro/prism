from typing import Optional, List

import aiohttp
from langchain_core.documents import Document
from pydantic import BaseModel

from prism.common.config import SETTINGS
from prism.operators.search import SearchOp

def sort_by_verified(docs: List[Document]) -> List[Document]:
    document_docs = [doc for doc in docs if isinstance(doc, Document)]
    sorted_document_docs = sorted(document_docs, key=lambda doc: not doc.metadata['verified'])
    return sorted_document_docs

class XSearchReq(BaseModel):
    query: str
    max_results: int = 30


class Media(BaseModel):
    type: str
    preview_image_url: str


class XSearchOp(SearchOp):

    async def search(self, input: XSearchReq) -> Optional[List[Document | Media]]:
        headers = {
            'Authorization': f'Bearer {SETTINGS.X_BEARER_TOKEN}'
        }

        search_url = "https://api.twitter.com/2/tweets/search/recent"
        query_params = {
            'query': input.query,
            'max_results': input.max_results,
            'tweet.fields': 'created_at,public_metrics,author_id',
            'expansions': 'attachments.media_keys,author_id',
            'media.fields': 'url,preview_image_url',
            'user.fields': 'name,profile_image_url,verified,verified_type',
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

                users_dict = {}
                if tweets.get('includes', None):
                    includes = tweets.get('includes')
                    users = includes.get('users', [])
                    for user in users:
                        users_dict[user["id"]] = user

                if tweets.get('data', None):
                    for tweet in tweets['data']:
                        author_info = users_dict.get(tweet.get("author_id", ""), {})

                        metadata = {
                            "content": tweet["text"],
                            "created_at": tweet.get("created_at", ""),
                            "query": input.query,
                            "site": "x",
                            "verified": author_info.get("verified", False),
                            "username": author_info.get("username", ""),
                            "profile_image_url": author_info.get("profile_image_url", ""),
                            "verified_type": author_info.get("verified_type", ""),
                        }

                        doc = Document(
                            page_content=tweet["text"],
                            metadata=metadata,
                        )
                        ret.append(doc)

                if tweets.get('includes', None):
                    includes = tweets.get('includes')
                    media = includes.get('media', [])
                    for media in media:
                        media_preview_image_url = media.get("preview_image_url", None)
                        media_type = media.get("type", None)
                        if media_preview_image_url and media_type:
                            ret.append(Media(type=media_type, preview_image_url=media_preview_image_url))

        return sort_by_verified(ret)
