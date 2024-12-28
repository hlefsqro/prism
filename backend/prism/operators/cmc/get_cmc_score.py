from datetime import datetime, timedelta

import aiohttp

from prism.common.config import SETTINGS

BITQUERY_URL = "https://graphql.bitquery.io/"

GRAPHQL_QUERY_TEMPLATE = {
    "ethereum": """
    query ($address: String!, $startTime: ISO8601DateTime!, $endTime: ISO8601DateTime!) {
      ethereum(network: ethereum) {
        transfers(
          currency: {is: $address}
          date: {between: [$startTime, $endTime]}
        ) {
          count
        }
      }
    }
    """,
    "solana": """
    query ($address: String!, $startTime: ISO8601DateTime!, $endTime: ISO8601DateTime!) {
      solana(network: solana) {
        transfers(
          currency: {is: $address}
          date: {between: [$startTime, $endTime]}
        ) {
          count
        }
      }
    }
    """,
    "base": """
    query ($address: String!, $startTime: ISO8601DateTime!, $endTime: ISO8601DateTime!) {
      base(network: base) {
        transfers(
          currency: {is: $address}
          date: {between: [$startTime, $endTime]}
        ) {
          count
        }
      }
    }
    """
}


async def execute_bitquery(chain, contract_address, start_time, end_time):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": SETTINGS.BITQUERY_API_KEY
    }

    query = GRAPHQL_QUERY_TEMPLATE.get(chain)
    if not query:
        raise ValueError(f"Unsupported chain: {chain}")

    variables = {
        "address": contract_address,
        "startTime": start_time,
        "endTime": end_time
    }

    payload = {
        "query": query,
        "variables": variables
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(BITQUERY_URL, json=payload, headers=headers) as response:
            if response.status != 200:
                raise ConnectionError(f"Query failed with status code {response.status}: {await response.text()}")
            result = await response.json()
            try:
                count = result["data"][chain]["transfers"][0]["count"]
                return int(count)
            except (KeyError, IndexError, TypeError) as e:
                print(f"Error parsing response for chain {chain}: {e}")
                return 0


def calculate_growth_percentage(start_count, end_count):
    if start_count == 0:
        return 0.0
    growth = ((end_count - start_count) / start_count) * 100
    return growth


def get_time_range(delta_hours_start, delta_hours_end):
    end_time = datetime.utcnow() - timedelta(hours=delta_hours_start)
    start_time = datetime.utcnow() - timedelta(hours=delta_hours_end)
    return start_time.isoformat() + "Z", end_time.isoformat() + "Z"


async def get_token_transaction_growth(token_address=None, platform=None):
    if not token_address or not isinstance(platform, dict):
        return None
    platform_name = platform.get("slug", "")
    if platform_name not in ["ethereum", "solana", "base"]:
        return None

    start_time_24h, end_time_24h = get_time_range(0, 24)
    start_time_48h, end_time_48h = get_time_range(24, 48)

    count_24h = await execute_bitquery(
        chain=platform_name,
        contract_address=token_address,
        start_time=start_time_24h,
        end_time=end_time_24h
    )

    count_48h_to_24h = await execute_bitquery(
        chain=platform_name,
        contract_address=token_address,
        start_time=start_time_48h,
        end_time=end_time_48h
    )

    growth_percentage = calculate_growth_percentage(count_48h_to_24h, count_24h)
    return growth_percentage
