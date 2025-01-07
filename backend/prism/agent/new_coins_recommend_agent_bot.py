from typing import List, Annotated, Optional, Type

from pydantic import BaseModel

from prism.agent import BaseGraphNode, state_overwrite, BaseGraphAgent
from prism.graph.filter_coins_graph_node import FilterCoinsGraphNode, FilterCoinsState
from prism.graph.rank_coins import RankCoinsGraphNode, RankCoinsState
from prism.graph.recall_market_cap_coins_graph_node import RecallMarketCapCoinsGraphNode, RecallMarketCapCoinsState
from prism.graph.search_derivative_new_coins_graph_node import SearchDerivativeNewCoinsState, \
    SearchDerivativeNewCoinsGraphNode


class NewCoinsRecommendReq(BaseModel):
    large_cap_million: int = 10
    large_cap_count: int = 10
    platform_slug: str = 'solana'


class NewCoinsRecommendResp(BaseModel):
    new_coins: List[dict]


class NewCoinsRecommendState(SearchDerivativeNewCoinsState,
                             RankCoinsState,
                             FilterCoinsState,
                             RecallMarketCapCoinsState):
    recall: Annotated[Optional[List[dict]], state_overwrite]
    large_cap_million: Annotated[Optional[int], state_overwrite]
    large_cap_count: Annotated[Optional[int], state_overwrite]
    platform_slug: Annotated[Optional[str], state_overwrite]

    large_cap_coins: Annotated[Optional[List[dict]], state_overwrite]


class NewCoinsRecommendBotAgent(BaseGraphAgent):

    def _get_state_type(self) -> Type:
        return NewCoinsRecommendState

    def _get_nodes(self) -> list[BaseGraphNode]:
        return [
            RecallMarketCapCoinsGraphNode(),
            FilterCoinsGraphNode(),
            SearchDerivativeNewCoinsGraphNode(),
            RankCoinsGraphNode()
        ]
