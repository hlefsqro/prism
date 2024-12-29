import logging

logger = logging.getLogger(__name__)


def select_evenly_spaced_elements(resources, num_elements=10, step=5):
    if not resources:
        return []
    selected_elements = [resources[i] for i in range(0, len(resources), step)]
    return selected_elements[:num_elements]


def score(pre, cur) -> float:
    if not pre:
        return 0
    if not cur:
        return 0
    if pre == 0:
        if cur == 0:
            return 0
        elif cur < 0:
            return -5
        else:
            return 5

    change_rate = (cur - pre) / pre * 100

    if change_rate < 0:
        if change_rate >= -20:
            return -1
        elif change_rate >= -40:
            return -2
        elif change_rate >= -60:
            return -3
        elif change_rate >= -80:
            return -4
        else:
            return -5
    else:
        if change_rate < 20:
            return 1
        elif change_rate < 40:
            return 2
        elif change_rate < 60:
            return 3
        elif change_rate < 80:
            return 4
        else:
            return 5


def merge_score(off_chain_score=0.0,
                crypto_platform_score=0.0,
                volume_score=0.0,
                market_cap_score=0.0) -> dict:
    ret = {
        "total_score": 0.0,
        "on_chain_score": 0.0,
        "off_chain_score": 0.0,
        "on_chain_platform_score": 0.0,
        "on_chain_symbol_volume_score": 0.0,
        "on_chain_symbol_market_cap_score": 0.0
    }
    try:
        if crypto_platform_score:
            ret["on_chain_platform_score"] = crypto_platform_score
        if volume_score:
            ret["on_chain_symbol_volume_score"] = volume_score
        if market_cap_score:
            ret["on_chain_symbol_market_cap_score"] = market_cap_score
        if off_chain_score:
            ret["off_chain_score"] = off_chain_score

        ret["on_chain_score"] = round((ret["on_chain_platform_score"] + ret["on_chain_symbol_volume_score"] + ret[
            "on_chain_symbol_market_cap_score"]) / 3, 2)
        ret["total_score"] = round((ret["on_chain_score"] + ret["off_chain_score"]) / 2, 2)

    except Exception as e:
        logger.error(e)

    return ret
