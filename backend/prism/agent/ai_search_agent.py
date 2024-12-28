import asyncio
from datetime import timedelta, datetime
from typing import AsyncGenerator, List

import pytz
from langchain_core.documents import Document

from prism.common.codec import jsondumps
from prism.common.utils import select_evenly_spaced_elements
from prism.operators.cmc.get_cmc_historical import GetCryptoHistoricalReq, GetCryptoHistorical
from prism.operators.cmc.get_cmc_latest import GetCryptoLatest, GetCryptoLatestReq
from prism.operators.cmc.get_cmc_score import get_token_transaction_growth
from prism.operators.llm import UserInputReq, EChartOpReq
from prism.operators.llm.google_mindmap_op import GoogleMindMapOp
from prism.operators.llm.query_rewriting_op import QueryRewritingOp
from prism.operators.llm.related_questions_op import RelatedQuestionsOp, RelatedQuestionsReq, Questions
from prism.operators.llm.search_answer_op import SearchAnswerOp, SearchAnswerReq
from prism.operators.llm.x_mindmap_op import XmindMapOp, XmindMapReq, TwitterSummaryResp
from prism.operators.search.searchapi import SearchApiOp, SearchApiReq
from prism.operators.search.x import XSearchOp, XSearchReq, Media
from prism.operators.search.x_count import XCountReq, XCountOp
from prism.repository.cmc_mapping import get_crypto_mapping, CmcCrypto


class AISearchSSE:

    @staticmethod
    def query_rewriting(data: list[str]):
        return {"event": "query_rewriting", "data": jsondumps(data)}

    @staticmethod
    def x_posts(data):
        list_r = []
        if data and isinstance(data, list):
            for d in data:
                if isinstance(d, Document):
                    list_r.append(d.metadata)

        return {"event": "x_posts", "data": jsondumps(list_r)}

    @staticmethod
    def google_answer(data: str):
        """"""
        return {"event": "google_answer", "data": data}

    @staticmethod
    def crypto(data: str):
        """"""
        return {"event": "crypto", "data": jsondumps(data)}

    @staticmethod
    def x_answer(data: str):
        """"""
        return {"event": "x_answer", "data": data}

    @staticmethod
    def related_questions(data: list[str]):
        return {"event": "related_questions", "data": jsondumps(data)}

    @staticmethod
    def mindmap(data: str):
        return {"event": "mindmap", "data": data}

    @staticmethod
    def images(data):
        return {"event": "images", "data": jsondumps(data)}

    @staticmethod
    def end():
        """"""
        return {"event": "end"}

    @staticmethod
    def crypto_latest(crypto_latest):
        return {"event": "crypto_latest", "data": jsondumps(crypto_latest)}

    @staticmethod
    def crypto_historical(crypto_latest):
        return {"event": "crypto_historical", "data": jsondumps(crypto_latest)}

    @staticmethod
    def x_query_growth_score(query_score):
        return {"event": "x_query_growth_score", "data": query_score}

    @staticmethod
    def token_transaction_growth(growth):
        return {"event": "token_transaction_growth", "data": growth}


class AISearchAgent(object):

    async def search(self, user_input: str) -> AsyncGenerator:
        org_user_input = user_input

        query_score_task = asyncio.create_task(self._get_query_score(org_user_input))
        crypto_task = asyncio.create_task(get_crypto_mapping(org_user_input))

        search_querys = set()
        search_querys.add(user_input)
        querys = await QueryRewritingOp().predict(UserInputReq(user_input=user_input))
        for q in (querys.queries or []):
            search_querys.add(q)

        yield AISearchSSE.query_rewriting(list(search_querys))

        x_search_tasks = [self._x_search_single_query(query) for query in [org_user_input]]

        crypto = await crypto_task

        get_token_transaction_growth_task = None
        if isinstance(crypto, CmcCrypto):
            yield AISearchSSE.crypto(crypto.model_dump())
            get_crypto_latest_task = asyncio.create_task(self._get_crypto_latest(crypto.id))
            get_crypto_historical_task = asyncio.create_task(self._get_crypto_historical(crypto.id))
            get_token_transaction_growth_task = asyncio.create_task(
                get_token_transaction_growth(crypto.ca, crypto.platform))

            yield AISearchSSE.crypto_latest(await get_crypto_latest_task)
            yield AISearchSSE.crypto_historical(await get_crypto_historical_task)

        x_search_results = await asyncio.gather(*x_search_tasks, return_exceptions=True)

        x_resources: List[Document] = []
        images: List[Media] = []

        for search_result in x_search_results:
            if isinstance(search_result, list):
                for x in search_result:
                    if isinstance(x, Document):
                        x_resources.append(x)
                    elif isinstance(x, Media):
                        images.append(x.model_dump())

        resources: List[Document] = []
        # resources.extend(searchapi_resources)
        resources.extend(x_resources)

        x_mindmap_task = asyncio.create_task(self._x_mindmap_op(x_resources=x_resources))

        yield AISearchSSE.x_posts(resources)

        related_questions_task = asyncio.create_task(
            self._gen_related_questions(user_input=user_input, resources=resources))

        # searchapi_answer = ""
        # async for chunk in SearchAnswerOp().stream(SearchAnswerReq(user_input=user_input,
        #                                                            resources=searchapi_resources, )):
        #     searchapi_answer += chunk
        #     yield AISearchSSE.google_answer(chunk)

        x_answer = ""
        async for chunk in SearchAnswerOp().stream(SearchAnswerReq(user_input=user_input,
                                                                   resources=x_resources, )):
            x_answer += chunk
            yield AISearchSSE.x_answer(chunk)

        yield AISearchSSE.images(images)

        related_questions = await related_questions_task
        yield AISearchSSE.related_questions(related_questions.questions)

        query_score = await query_score_task
        yield AISearchSSE.x_query_growth_score(query_score)

        if get_token_transaction_growth_task:
            token_transaction_growth = await get_token_transaction_growth_task
            if token_transaction_growth:
                yield AISearchSSE.token_transaction_growth(token_transaction_growth)

        # google_mindmap_task = asyncio.create_task(self._google_mindmap_op(searchapi_answer=searchapi_answer))

        # google_mindmap = await google_mindmap_task
        x_mindmap = await x_mindmap_task

        mindmap = f"# {org_user_input}\n\n"
        # if isinstance(google_mindmap, TreeMindmap):
        #     mindmap += f"## Web Search\n\n"
        #     mindmap += google_mindmap.to_markdown()
        #
        #     mindmap += "\n\n"
        if isinstance(x_mindmap, TwitterSummaryResp):
            mindmap += f"## X\n\n"
            for s in x_mindmap.summaries:
                mindmap += f"- {s.twitter_user_name} : {s.content_summary}\n\n"

        yield AISearchSSE.mindmap(mindmap)

        yield AISearchSSE.end()

    async def _google_mindmap_op(self, searchapi_answer: str):
        return await GoogleMindMapOp().predict(EChartOpReq(text=searchapi_answer))

    async def _x_mindmap_op(self, x_resources):
        return await XmindMapOp().predict(XmindMapReq(resources=select_evenly_spaced_elements(x_resources, 10)))

    async def _x_search_single_query(self, query: str):
        return await XSearchOp().search(XSearchReq(query=query))

    async def _searchapi_search_single_query(self, query: str):
        return await SearchApiOp().search(SearchApiReq(query=query))

    async def _gen_related_questions(self, user_input: str, resources) -> Questions:
        return await RelatedQuestionsOp().predict(RelatedQuestionsReq(user_input=user_input, resources=resources))

    async def _get_crypto_latest(self, id):
        return await GetCryptoLatest().call(GetCryptoLatestReq(id=id))

    async def _get_crypto_historical(self, id):
        now = datetime.now(pytz.utc)
        one_hour_ago = now - timedelta(hours=1)
        return await GetCryptoHistorical().call(GetCryptoHistoricalReq(id=str(id),
                                                                       time_start=str(one_hour_ago),
                                                                       time_end=str(now)))

    async def _get_query_score(self, query: str):
        try:
            now = datetime.now(pytz.utc)
            end_1 = (now - timedelta(minutes=30)).isoformat()
            begin_1 = (now - timedelta(minutes=60)).isoformat()

            end_2 = (now - timedelta(minutes=90)).isoformat()
            begin_2 = (now - timedelta(minutes=120)).isoformat()

            r1 = await XCountOp().search(XCountReq(query=query, start_time=begin_1, end_time=end_1))
            r2 = await XCountOp().search(XCountReq(query=query, start_time=begin_2, end_time=end_2))

            if r2 >= 100 and r1 >= 100:
                return 3

            if r2 == 0 and r1 == 0:
                return 0

            change_percentage = ((r1 - r2) / r2) * 100

            if change_percentage >= 80:
                return 5
            elif change_percentage >= 60:
                return 4
            elif change_percentage >= 40:
                return 3
            elif change_percentage >= 20:
                return 2
            elif change_percentage > 0:
                return 1
            else:
                return 0
        except Exception:
            return 0
