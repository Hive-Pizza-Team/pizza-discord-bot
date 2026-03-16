"""Utility helpers related to hive-engine."""
from typing import Dict, List, Optional

from hiveengine.api import Api
from hiveengine.market import Market
from hiveengine.tokenobject import Token

from config import load_config
from utils_hive import get_hive_instance

_hiveengine_api: Optional[Api] = None
_market: Optional[Market] = None


def get_hiveengine_instance() -> Api:
    global _hiveengine_api
    if _hiveengine_api is None:
        cfg = load_config()
        _hiveengine_api = Api(
            url=cfg.hive_engine_api_node,
            rpcurl=cfg.hive_engine_api_node_rpc,
        )
    return _hiveengine_api


def get_hiveengine_market_instance() -> Market:
    global _market
    if _market is None:
        _market = Market(
            api=get_hiveengine_instance(),
            blockchain_instance=get_hive_instance(),
        )
    return _market


def get_market_history(symbol: str,
                       market: Optional[Market] = None) -> List[Dict]:
    """Get market history for a Hive-Engine token."""
    if market is None:
        market = get_hiveengine_market_instance()
    order_count = 1000
    orders: List[Dict] = []
    while order_count == 1000:
        response = market.get_trades_history(
            symbol, limit=1000, offset=len(orders))
        order_count = len(response)
        orders += response

    return orders


def get_token_holders(symbol: str,
                      api: Optional[Api] = None) -> List[Dict]:
    """Get a list of wallets holding a Hive-Engine token."""
    if api is None:
        api = get_hiveengine_instance()
    holder_count = 1000
    token_holders: List[Dict] = []
    token = Token(symbol, api=api)
    while holder_count == 1000:
        response = token.get_holder(offset=len(token_holders))
        holder_count = len(response)
        token_holders += response

    return token_holders
