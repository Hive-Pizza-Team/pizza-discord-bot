"""Centralized configuration for the pizza discord bot."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    discord_token: str
    hive_engine_api_node: str
    hive_engine_api_node_rpc: str
    hivesearcher_api_key: str
    hive_api_nodes: tuple


def load_config() -> Config:
    load_dotenv()
    nodes_str = os.getenv(
        'HIVE_API_NODES',
        'https://api.deathwing.me,https://api.hive.blog',
    )
    return Config(
        discord_token=os.getenv('DISCORD_TOKEN', ''),
        hive_engine_api_node=os.getenv('HIVE_ENGINE_API_NODE', ''),
        hive_engine_api_node_rpc=os.getenv('HIVE_ENGINE_API_NODE_RPC', ''),
        hivesearcher_api_key=os.getenv('HIVESEARCHER_API_KEY', ''),
        hive_api_nodes=tuple(n.strip() for n in nodes_str.split(',')),
    )
