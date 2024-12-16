from typing import Optional, List

from pydantic import BaseModel, Field, field_validator
from pyecharts.charts import Tree
from pyecharts.charts.base import Base

from prism.operators.llm import EChartOp, EChartOpReq

DEFAULT_HUMAN_PROMPT = """\
你是非常出色的数据提取助手。你的具体任务是从文本中提取出绘制树型思维导图所需的结构化数据。

文本如下：

{text}\
"""


class TreeMindmap(BaseModel):
    """树型思维导图"""
    name: str = Field(default="", description="节点描述")
    children: Optional[List["TreeMindmap"]] = Field(default=None, description="子节点，类型和 TreeMindmap 一样")

    @field_validator('children', mode='before')
    def validator_children(cls, v):
        if isinstance(v, list):
            if not v:
                return None
            return v
        return None


class TreeMindMapEchartOp(EChartOp):
    default_human_prompt: str = DEFAULT_HUMAN_PROMPT
    llm_output_model: type[BaseModel] | str = TreeMindmap

    async def _to_chart(self, input: EChartOpReq, llm_output: Optional[TreeMindmap]) -> Optional[Base]:
        if not isinstance(llm_output, TreeMindmap):
            return None

        tree = (
            Tree()
            .add("", data=[llm_output.model_dump(exclude_none=True)], )
        )
        return tree
