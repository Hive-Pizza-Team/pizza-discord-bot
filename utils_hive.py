"""Utility helpers related to Hive blockchain."""
import beem

from config import load_config

_hive_instance = None


def get_hive_instance():
    global _hive_instance
    if _hive_instance is None:
        cfg = load_config()
        _hive_instance = beem.Hive(node=list(cfg.hive_api_nodes))
        beem.instance.set_shared_blockchain_instance(_hive_instance)
    return _hive_instance


def get_hive_power_delegations(wallet, hive=None):
    """Get a total of incoming HP delegation to wallet."""
    if hive is None:
        hive = get_hive_instance()
    acc = beem.account.Account(wallet, blockchain_instance=hive)

    incoming_delegations_total = 0

    delegations = acc.get_vesting_delegations()

    for delegation in delegations:
        hive_power = hive.vests_to_token_power(
            delegation['vesting_shares']['amount']) / 10 ** delegation['vesting_shares']['precision']
        incoming_delegations_total += hive_power

    return incoming_delegations_total
