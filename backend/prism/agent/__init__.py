import requests


async def recall_market_cap_coins(large_cap_million):
    params = {
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1
    }
    all_coins = []
    while True:
        response = requests.get(params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        large_cap_coins = [coin for coin in data if coin.get("market_cap", 0) > large_cap_million]
        all_coins.extend(large_cap_coins)
        params["page"] += 1
    return all_coins


async def filter_coins_by_platform(coins):
    solana_coins = []
    for coin in coins:
        coin_id = coin["id"]
        platforms = {}.get("platforms", {})
        if "solana" in platforms:
            solana_coins.append({
                "id": coin_id,
                "name": coin["name"],
                "symbol": coin["symbol"],
                "solana_address": platforms["solana"]
            })
    return solana_coins


async def search_derivative_new_coins():
    params = {
        "type": "token"
    }
    headers = {"Authorization": ""}
    response = requests.get(headers=headers, params=params)
    response.raise_for_status()
    return response.json()


async def rank_coins(market_data):
    filtered = [token for token in market_data if 6000 <= token["market_cap"] <= 20000]
    sorted_tokens = sorted(filtered, key=lambda x: x["total_volume"], reverse=True)
    return sorted_tokens[:10]
