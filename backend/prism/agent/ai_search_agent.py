import asyncio
from typing import AsyncGenerator, List

from langchain_core.documents import Document

from prism.operators.llm import UserInputReq, EChartOpReq, EChartOpResp
from prism.operators.llm.echarts_tree_op import TreeMindMapEchartOp
from prism.operators.llm.query_rewriting_op import QueryRewritingOp
from prism.operators.llm.related_questions_op import RelatedQuestionsOp, RelatedQuestionsReq, Questions
from prism.operators.llm.search_answer_op import SearchAnswerOp, SearchAnswerReq
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
    def echarts(data: dict):
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

        yield AISearchSSE.query_rewriting(search_querys)

        x_search_tasks = [self._x_search_single_query(query) for query in search_querys]
        x_search_results = await asyncio.gather(*x_search_tasks, return_exceptions=True)

        resources: List[Document] = []

        for x_search_ret in x_search_results:
            if isinstance(x_search_ret, list) and x_search_ret:
                for x in x_search_ret:
                    if isinstance(x, Document):
                        resources.append(x)
                        yield AISearchSSE.resources(x.model_dump_json(exclude_none=True))

        related_questions_task = asyncio.create_task(
            self._gen_related_questions(user_input=user_input, resources=resources))

        answer = ""

        async for chunk in SearchAnswerOp().stream(SearchAnswerReq(user_input="介绍特朗普",
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

    async def _gen_related_questions(self, user_input: str, resources) -> Questions:
        return await RelatedQuestionsOp().predict(RelatedQuestionsReq(user_input=user_input, resources=resources))
