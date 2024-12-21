import asyncio
from typing import AsyncGenerator, List

from langchain_core.documents import Document

from prism.operators.llm import UserInputReq, EChartOpReq, EChartOpResp
from prism.operators.llm.echarts_tree_op import TreeMindMapEchartOp
from prism.operators.llm.query_rewriting_op import QueryRewritingOp
from prism.operators.llm.related_questions_op import RelatedQuestionsOp, RelatedQuestionsReq, Questions
from prism.operators.llm.search_answer_op import SearchAnswerOp, SearchAnswerReq
from prism.operators.search.searchapi import SearchApiOp, SearchApiReq
from prism.operators.search.x import XSearchOp, XSearchReq


class AISearchSSE:

    @staticmethod
    def query_rewriting(data: list[str]):
        return {"event": "query_rewriting", "data": data}

    @staticmethod
    def resources(json_str: str):
        return {"event": "resources", "data": json_str}

    @staticmethod
    def answer(data: str):
        """"""
        return {"event": "answer", "data": data}

    @staticmethod
    def related_questions(data: list[str]):
        return {"event": "related_questions", "data": data}

    @staticmethod
    def echarts(data: str):
        return {"event": "echarts", "data": data}

    @staticmethod
    def end():
        """"""
        return {"event": "end"}


class AISearchAgent(object):

    async def search(self, user_input: str) -> AsyncGenerator:
        search_querys = set()
        search_querys.add(user_input)
        querys = await QueryRewritingOp().predict(UserInputReq(user_input=user_input))
        if querys and querys.queries:
            for user_input in querys.queries:
                search_querys.add(user_input)

        search_querys = list(search_querys)
        yield AISearchSSE.query_rewriting(search_querys)

        x_search_tasks = [self._x_search_single_query(query) for query in search_querys]
        searchapi_search_tasks = [self._searchapi_search_single_query(query) for query in search_querys]

        search_results = []

        x_search_results = await asyncio.gather(*x_search_tasks, return_exceptions=True)
        searchapi_search_results = await asyncio.gather(*searchapi_search_tasks, return_exceptions=True)

        search_results.extend(x_search_results)
        search_results.extend(searchapi_search_results)

        resources: List[Document] = []

        for search_ret in search_results:
            if isinstance(search_ret, list) and search_ret:
                for x in search_ret:
                    if isinstance(x, Document):
                        resources.append(x)
                        yield AISearchSSE.resources(x.model_dump_json(exclude_none=True))
            elif isinstance(search_ret, Document) and search_ret:
                resources.append(search_ret)
                yield AISearchSSE.resources(search_ret.model_dump_json(exclude_none=True))

        related_questions_task = asyncio.create_task(
            self._gen_related_questions(user_input=user_input, resources=resources))

        answer = ""

        async for chunk in SearchAnswerOp().stream(SearchAnswerReq(user_input=user_input,
                                                                   resources=resources, )):
            answer += chunk
            yield AISearchSSE.answer(chunk)

        related_questions = await related_questions_task
        yield AISearchSSE.related_questions(related_questions.questions)

        mindmap = await TreeMindMapEchartOp().predict(EChartOpReq(text=answer))
        if isinstance(mindmap, EChartOpResp):
            yield AISearchSSE.echarts(mindmap.options)

        yield AISearchSSE.end()

    async def _x_search_single_query(self, query: str):
        return await XSearchOp().search(XSearchReq(query=query))

    async def _searchapi_search_single_query(self, query: str):
        return await SearchApiOp().search(SearchApiReq(query=query))

    async def _gen_related_questions(self, user_input: str, resources) -> Questions:
        return await RelatedQuestionsOp().predict(RelatedQuestionsReq(user_input=user_input, resources=resources))


SearchApiOp
