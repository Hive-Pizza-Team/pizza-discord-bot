"""Utility helpers related to Hive blockchain."""
import beem

HIVE = beem.Hive(node=['https://api.deathwing.me', 'https://api.hive.blog'])
beem.instance.set_shared_blockchain_instance(HIVE)


def get_hive_power_delegations(wallet):
    """Get a total of incoming HP delegation to wallet."""
    acc = beem.account.Account(wallet, blockchain_instance=HIVE)

    incoming_delegations_total = 0

    delegations = acc.get_vesting_delegations()

    for delegation in delegations:
        hive_power = HIVE.vests_to_token_power(
            delegation['vesting_shares']['amount']) / 10 ** delegation['vesting_shares']['precision']
        incoming_delegations_total += hive_power

    return incoming_delegations_total


def get_hive_instance():
    return HIVE
