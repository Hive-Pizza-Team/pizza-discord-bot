"""Utility helpers related to hive-engine."""
from hiveengine.api import Api
from hiveengine.market import Market
from hiveengine.tokenobject import Token

from config import load_config
from utils_hive import get_hive_instance

_hiveengine_api = None
_market = None


def get_hiveengine_instance():
    global _hiveengine_api
    if _hiveengine_api is None:
        cfg = load_config()
        _hiveengine_api = Api(url=cfg.hive_engine_api_node, rpcurl=cfg.hive_engine_api_node_rpc)
    return _hiveengine_api


def get_hiveengine_market_instance():
    global _market
    if _market is None:
        _market = Market(api=get_hiveengine_instance(), blockchain_instance=get_hive_instance())
    return _market


def get_market_history(symbol, market=None):
    """Get market history for a Hive-Engine token."""
    if market is None:
        market = get_hiveengine_market_instance()
    order_count = 1000
    orders = []
    while order_count == 1000:
        response = market.get_trades_history(
            symbol, limit=1000, offset=len(orders))
        order_count = len(response)
        orders += response

    return orders


def get_token_holders(symbol, api=None):
    """Get a list of wallets holding a Hive-Engine token."""
    if api is None:
        api = get_hiveengine_instance()
    holder_count = 1000
    token_holders = []
    token = Token(symbol, api=api)
    while holder_count == 1000:
        response = token.get_holder(offset=len(token_holders))
        holder_count = len(response)
        token_holders += response

    return token_holders
