import asyncio
from typing import AsyncGenerator, List

from langchain_core.documents import Document

from prism.common.codec import jsondumps
from prism.common.utils import select_evenly_spaced_elements
from prism.operators.llm import UserInputReq, EChartOpReq
from prism.operators.llm.google_mindmap_op import GoogleMindMapOp, TreeMindmap
from prism.operators.llm.query_rewriting_op import QueryRewritingOp
from prism.operators.llm.related_questions_op import RelatedQuestionsOp, RelatedQuestionsReq, Questions
from prism.operators.llm.search_answer_op import SearchAnswerOp, SearchAnswerReq
from prism.operators.llm.x_mindmap_op import XmindMapOp, XmindMapReq, TwitterSummaryResp
from prism.operators.search.searchapi import SearchApiOp, SearchApiReq
from prism.operators.search.x import XSearchOp, XSearchReq


class AISearchSSE:

    @staticmethod
    def query_rewriting(data: list[str]):
        return {"event": "query_rewriting", "data": jsondumps(data)}

    @staticmethod
    def resources(json_str: str):
        return {"event": "resources", "data": json_str}

    @staticmethod
    def google_answer(data: str):
        """"""
        return {"event": "google_answer", "data": data}

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
    def end():
        """"""
        return {"event": "end"}


class AISearchAgent(object):

    async def search(self, user_input: str) -> AsyncGenerator:
        org_user_input = user_input
        search_querys = set()
        search_querys.add(user_input)
        querys = await QueryRewritingOp().predict(UserInputReq(user_input=user_input))
        if querys and querys.queries:
            for user_input in querys.queries:
                search_querys.add(user_input)

        search_querys = list(search_querys)
        yield AISearchSSE.query_rewriting(search_querys)

        x_search_tasks = [self._x_search_single_query(query) for query in search_querys]
        # searchapi_search_tasks = [self._searchapi_search_single_query(query) for query in search_querys]

        x_search_results = await asyncio.gather(*x_search_tasks, return_exceptions=True)
        # searchapi_search_results = await asyncio.gather(*searchapi_search_tasks, return_exceptions=True)

        # searchapi_resources: List[Document] = []
        # for search_result in searchapi_search_results:
        #     if isinstance(search_result, Document):
        #         searchapi_resources.append(search_result)

        x_resources: List[Document] = []
        for search_result in x_search_results:
            if isinstance(search_result, list):
                for x in search_result:
                    if isinstance(x, Document):
                        x_resources.append(x)

        resources: List[Document] = []
        # resources.extend(searchapi_resources)
        resources.extend(x_resources)

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

        related_questions = await related_questions_task
        yield AISearchSSE.related_questions(related_questions.questions)

        # google_mindmap_task = asyncio.create_task(self._google_mindmap_op(searchapi_answer=searchapi_answer))
        x_mindmap_task = asyncio.create_task(self._x_mindmap_op(x_resources=x_resources))

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
