import asyncio

from prism.agent.new_coins_recommend_agent_bot import NewCoinsRecommendBotAgent, NewCoinsRecommendReq


async def main():
    ret = await NewCoinsRecommendBotAgent().call(NewCoinsRecommendReq())
    print(ret)


asyncio.run(main())
