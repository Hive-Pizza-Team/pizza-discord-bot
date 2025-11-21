"""Utility helpers related to hive-engine."""
from dotenv import load_dotenv
from hiveengine.api import Api
from hiveengine.market import Market
from hiveengine.tokenobject import Token
from hiveengine.wallet import Wallet
import os

from utils_hive import get_hive_instance

load_dotenv()
HIVE_ENGINE_API_NODE = os.getenv('HIVE_ENGINE_API_NODE')
HIVE_ENGINE_API_NODE_RPC = os.getenv('HIVE_ENGINE_API_NODE_RPC')
hiveengine_api = Api(url=HIVE_ENGINE_API_NODE, rpcurl=HIVE_ENGINE_API_NODE_RPC)
market = Market(api=hiveengine_api, blockchain_instance=get_hive_instance())


def get_market_history(symbol):
    """Get market history for a Hive-Engine token."""
    order_count = 1000
    orders = []
    while order_count == 1000:
        response = market.get_trades_history(
            symbol, limit=1000, offset=len(orders))
        order_count = len(response)
        orders += response

    return orders


def get_token_holders(symbol):
    """Get a list of wallets holding a Hive-Engine token."""
    holder_count = 1000
    token_holders = []
    token = Token(symbol, api=hiveengine_api)
    while holder_count == 1000:
        response = token.get_holder(offset=len(token_holders))
        holder_count = len(response)
        token_holders += response

    return token_holders


def get_hiveengine_instance():
    return hiveengine_api


def get_hiveengine_market_instance():
    return market
