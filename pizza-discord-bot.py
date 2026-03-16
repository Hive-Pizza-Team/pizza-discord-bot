#!/usr/bin/env python3
"""Discord bot for Hive Pizza community."""
import beem
from beem.witness import Witness, WitnessesRankedByVote
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands, tasks
import hiveengine
from hiveengine.wallet import Wallet
import json as json_lib
import logging
import os
from dotenv import load_dotenv
import random

import requests
import sys
import traceback

from typing import Literal, Optional


from config import load_config
from utils import *
from utils_hiveengine import *
from utils_hive import *

load_dotenv()

logger = logging.getLogger(__name__)

# Load GIF data from external JSON file
_gif_data_path = os.path.join(os.path.dirname(__file__), 'data', 'gifs.json')
with open(_gif_data_path) as _f:
    GIF_DATA = json_lib.load(_f)

DEFAULT_TOKEN_NAME = 'PIZZA'
DEFAULT_DIESEL_POOL = 'PIZZA:ONEUP'
DEFAULT_GIF_CATEGORY = 'PIZZA'


async def update_bot_user_status(bot):
    """Update the bot's status."""
    # last_price = float(get_market_history(symbol=DEFAULT_TOKEN_NAME)[-1]['price'])
    last_price_usd = round(get_coin_price()[0], 3)

    # from datetime import datetime
    # date_obj = datetime.fromisoformat('2025-11-19T13:00:00+00:00')
    # now = datetime.now(date_obj.tzinfo)
    # delta = date_obj - now
    # days = delta.days
    # seconds_remaining = delta.seconds
    # hours = seconds_remaining // 3600
    # minutes = (seconds_remaining % 3600) // 60
    # seconds = (seconds_remaining % 60)

    if bot:
        # await bot.change_presence(activity=discord.Game('HF28 ~ %dd %dh %dm %ds' % (days,hours,minutes,seconds)))
        await bot.change_presence(activity=discord.Game('HIVE ~ $%.3f' % last_price_usd))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!!!",
                   intents=intents)


class PizzaCog(commands.Cog):
    """This is a cog to peridiocally update the bot status."""

    def __init__(self, bot):
        """Constructor."""
        self.price_check.start()
        self.bot = bot

    def cog_unload(self):
        """Stop the task loop on shutdown."""
        self.price_check.cancel()

    @tasks.loop(minutes=16.0)
    async def price_check(self):
        """Task to run every N execution."""
        if self.bot.user:
            await update_bot_user_status(self.bot)


# Bot commands
@bot.tree.command(name="bal", description="Print Hive-Engine wallet balances.")
@app_commands.describe(
    wallet='Hive wallet name, i.e. hive.pizza.',
    symbol='Hive-Engine token symbol, i.e. PIZZA.',
)
async def bal(ctx: discord.Interaction, wallet: str, symbol: str = ''):
    """<wallet> <symbol> : Print Hive-Engine wallet balances."""
    if not symbol:
        symbol = determine_native_token(ctx, DEFAULT_TOKEN_NAME)

    symbol = symbol.upper()
    wallet = wallet.lower()

    if symbol.lower() == 'hive':
        acc = beem.account.Account(wallet)
        balance = acc.available_balances[0]
        staked = acc.get_token_power(only_own_vests=True)
        delegation_out = get_hive_power_delegations(wallet)
        delegation_in = acc.get_token_power() + delegation_out - staked

    else:
        # hive engine token
        wallet_token_info = Wallet(
            wallet, blockchain_instance=get_hive_instance(), api=get_hiveengine_instance()).get_token(symbol)

        if not wallet_token_info:
            balance = 0
            staked = 0
            delegation_in = 0
            delegation_out = 0
        else:
            balance = float(wallet_token_info['balance'])
            staked = float(wallet_token_info['stake'])
            delegation_in = float(wallet_token_info['delegationsIn'])
            delegation_out = float(wallet_token_info['delegationsOut'])

    embed = make_embed(title='Balances for @%s' %
                       wallet, description='$%s' % symbol)
    embed.add_field(name='Liquid', value='%0.3f' % (balance), inline=False)
    embed.add_field(name='Staked', value='%0.3f' % (staked), inline=False)

    if delegation_in > 0:
        embed.add_field(name='Incoming Delegation', value='%0.3f' %
                        (delegation_in), inline=False)
    if delegation_out > 0:
        embed.add_field(name='Outgoing Delegation', value='%0.3f' %
                        (delegation_out), inline=False)

    total = balance + staked + delegation_in - delegation_out
    embed.add_field(name='Total', value='%0.3f' % (total), inline=False)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="bals", description="Print Hive-Engine wallet balances.")
@app_commands.describe(
    wallet='Hive wallet name, i.e. hive.pizza.'
)
async def bals(ctx: discord.Interaction, wallet: str):
    """<wallet>: Print Hive-Engine wallet balances."""
    # hive engine token
    wallet = wallet.lower()
    wallet_token_info = None

    try:
        wallet_token_info = Wallet(
            wallet, blockchain_instance=get_hive_instance(), api=get_hiveengine_instance())
    except beem.exceptions.AccountDoesNotExistsException:
        await ctx.response.send_message('Error: the wallet doesnt exist.')
        return

    # sort by stake then balance
    wallet_token_info.sort(key=lambda elem: float(
        elem['stake']) + float(elem['balance']), reverse=True)

    longest_symbol_len = 0
    for token in wallet_token_info:
        if len(token['symbol']) > longest_symbol_len:
            longest_symbol_len = len(token['symbol'])

    message_body = '```'
    message_body += 'SYMBOL'.ljust(longest_symbol_len, ' ') + \
        ' |  LIQUID  |  STAKED  | INCOMING | OUTGOING\n'

    rows = []

    for token in wallet_token_info:
        symbol = token['symbol']
        balance = float(token['balance'])
        staked = float(token['stake'])
        delegation_in = float(token['delegationsIn'])
        delegation_out = float(token['delegationsOut'])

        if balance + staked + delegation_in + delegation_out == 0.0:
            continue

        padded_symbol = symbol.ljust(longest_symbol_len, ' ')
        rows.append('%s |%10.3f|%10.3f|%10.3f|%9.3f\n' % (
            padded_symbol, balance, staked, delegation_in, delegation_out))

    for row in rows[0:10]:
        message_body += row

    message_body += '```'

    embed = make_embed(title='First 10 balances for @%s' %
                       wallet, description=message_body)
    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="price", description="Print Hive-Engine / CoinGecko market price info.")
@app_commands.describe(
    symbol='Hive-Engine token symbol, i.e. PIZZA.',
)
async def price(ctx: discord.Interaction, symbol: str = ''):
    """<symbol> : Print Hive-Engine / CoinGecko market price info."""
    if not symbol:
        symbol = determine_native_token(ctx, DEFAULT_TOKEN_NAME)

    embed = get_token_price_he_cg(symbol)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="gif", description="Show a gif!")
@app_commands.describe(
    category="name of a gif category"
)
async def gif(ctx: discord.Interaction, category: str = ''):
    """Drop a random GIF! Or choose a category of gifs."""

    gif_set = GIF_DATA.get(category.lower(), GIF_DATA['pizza']) if category else GIF_DATA['pizza']

    gif_url = random.choice(gif_set)
    await ctx.response.send_message(gif_url)


@bot.tree.command(name="info", description="Print Hive.Pizza project link.")
async def info(ctx: discord.Interaction):
    """Print Hive.Pizza project link."""
    response = '''Learn more about $PIZZA @ https://hive.pizza'''
    await ctx.response.send_message(response)


@bot.tree.command(name="tokenomics", description="Print Hive-Engine token distribution info.")
@app_commands.describe(
    symbol="Hive-Engine token symbol. i.e. PIZZA."
)
async def tokenomics(ctx: discord.Interaction, symbol: str = ''):
    """<symbol> : Print Hive-Engine token distribution info."""
    await ctx.response.send_message("... thinking ...")

    if not symbol:
        symbol = determine_native_token(ctx, DEFAULT_TOKEN_NAME)
    symbol = symbol.upper()

    try:
        wallets = get_token_holders(
            symbol)
    except hiveengine.exceptions.TokenDoesNotExists:
        await ctx.edit_original_response('Error: the Hive-Engine token symbol does not exist.')
        return

    total_wallets = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) > 0])

    # count wallets with at least 1 token
    wallets_1plus = len([  # noqa: F841
        x for x in wallets
        if float(x['balance']) + float(x['stake']) >= 1
    ])

    # count wallets with at least 20 tokens
    wallets_20plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 20])

    # count wallets with at least 200 tokens
    wallets_200plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 200])

    # count wallets with at least 1,000 tokens
    wallets_1000plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 1000])

    # count wallets with at least 3,000 tokens
    wallets_3000plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 3000])

    # count wallets with at least 5,000 tokens
    wallets_5000plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 5000])

    # count wallets with at least 10,000 tokens
    wallets_10000plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 10000])

    # count wallets with at least 100,000 tokens
    wallets_100000plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 100000])

    # count wallets with at least 1,000,000 tokens
    wallets_1000000plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 1000000])

    # count wallets with at least 10,000,000 tokens
    wallets_10000000plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 10000000])

    # count wallets with at least 100,000,000 tokens
    wallets_100000000plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 100000000])

    message = '''```
%.4d wallets hold >            0 $%s
%.4d wallets hold >=          20 $%s
%.4d wallets hold >=         200 $%s
%.4d wallets hold >=       1,000 $%s
%.4d wallets hold >=       3,000 $%s
%.4d wallets hold >=       5,000 $%s
%.4d wallets hold >=      10,000 $%s
%.4d wallets hold >=     100,000 $%s
%.4d wallets hold >=   1,000,000 $%s
%.4d wallets hold >=  10,000,000 $%s
%.4d wallets hold >= 100,000,000 $%s
```''' % (total_wallets, symbol, wallets_20plus, symbol, wallets_200plus, symbol, wallets_1000plus, symbol, wallets_3000plus, symbol, wallets_5000plus, symbol, wallets_10000plus, symbol, wallets_100000plus, symbol, wallets_1000000plus, symbol, wallets_10000000plus, symbol, wallets_100000000plus, symbol)

    embed = make_embed(title='$%s Token Distribution' %
                       symbol, description=message)
    await ctx.edit_original_response(embed=embed)


@bot.tree.command(name="top10", description="Print Hive-Engine token rich list top 10.")
@app_commands.describe(
    symbol="Hive-Engine token symbol. i.e. PIZZA."
)
async def top10(ctx: discord.Interaction, symbol: str = ''):
    """<symbol> : Print Hive-Engine token rich list top 10."""
    await ctx.response.send_message("... thinking ...")

    if not symbol:
        symbol = determine_native_token(ctx, DEFAULT_TOKEN_NAME)

    try:
        accounts = get_token_holders(
            symbol)
    except hiveengine.exceptions.TokenDoesNotExists:
        await ctx.response.send_message('Error: the Hive-Engine token symbol does not exist.')
        return

    # identify the top 10 token holders
    symbol = symbol.upper()

    embed = make_embed(title='Top 10 $%s Holders' % symbol)

    accounts_stake = sorted(
        accounts, key=lambda a: float(a['stake']), reverse=True)
    top10stake = [(x['account'], float(x['stake']))
                  for x in accounts_stake[0:10]]
    count = 0
    stake_string = ''
    for account, stake in top10stake:
        count += 1
        stake_string += '%d. %s - %0.3f\n' % (count, account, stake)
    embed.add_field(name='Top 10 $%s Staked' %
                    symbol, value=stake_string, inline=True)

    accounts_liquid = sorted(
        accounts, key=lambda a: float(a['balance']), reverse=True)
    top10liquid = [(x['account'], float(x['balance']))
                   for x in accounts_liquid[0:10]]
    count = 0
    liquid_string = ''
    for account, liquid in top10liquid:
        count += 1
        liquid_string += '%d. %s - %0.3f\n' % (count, account, liquid)
    embed.add_field(name='Top 10 $%s Liquid' %
                    symbol, value=liquid_string, inline=True)

    accounts_total = sorted(accounts, key=lambda a: float(
        a['stake']) + float(a['balance']), reverse=True)
    top10total = [(x['account'], float(x['stake']) + float(x['balance']))
                  for x in accounts_total[0:10]]
    count = 0
    total_string = ''
    for account, total in top10total:
        count += 1
        total_string += '%d. %s - %0.3f\n' % (count, account, total)
    embed.add_field(name='Top 10 $%s Total' %
                    symbol, value=total_string, inline=True)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="history", description="Print Hive-Engine market trade history.")
@app_commands.describe(
    symbol="Hive-Engine token symbol. i.e. PIZZA."
)
async def history(ctx: discord.Interaction, symbol: str = ''):
    """<symbol> : Print recent Hive-Engine token trade history."""
    if symbol == '':
        symbol = determine_native_token(ctx, DEFAULT_TOKEN_NAME)

    message = '''```fix
'''
    try:
        for tx in get_market_history(symbol)[::-1][0:10]:
            message += '%0.4f @ %0.4f HIVE: %s -> %s\n' % (
                float(tx['quantity']), float(tx['price']), tx['seller'], tx['buyer'])
    except hiveengine.exceptions.TokenDoesNotExists:
        await ctx.response.send_message('Error: the Hive-Engine token symbol does not exist.')
        return

    message += '```'

    embed = make_embed(title='Latest 10 $%s Hive-Engine Transactions' %
                       symbol, description=message)
    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="witness", description="Print Hive Witness Info.")
@app_commands.describe(
    witnessname="Name of Hive witness."
)
async def witness(ctx: discord.Interaction, witnessname: str = 'pizza.witness'):
    """<witness name>: Print Hive Witness Info."""
    witnessname = witnessname.lower()
    message_body = '```\n'  # noqa: F841

    witness = Witness(witnessname, blockchain_instance=get_hive_instance())

    witness_json = witness.json()
    witness_schedule = get_hive_instance().get_witness_schedule()
    config = get_hive_instance().get_config()
    if "VIRTUAL_SCHEDULE_LAP_LENGTH2" in config:
        lap_length = int(config["VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    elif "HIVE_VIRTUAL_SCHEDULE_LAP_LENGTH2" in config:
        lap_length = int(config["HIVE_VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    else:
        lap_length = int(config["STEEM_VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    rank = 0
    active_rank = 0
    found = False
    witnesses = WitnessesRankedByVote(limit=101, blockchain_instance=get_hive_instance())
    vote_sum = witnesses.get_votes_sum()
    for w in witnesses:
        rank += 1
        if w.is_active:
            active_rank += 1
        if w["owner"] == witness["owner"]:
            found = True
            break
    virtual_time_to_block_num = int(
        witness_schedule["num_scheduled_witnesses"]) / (lap_length / (vote_sum + 1))

    virtual_diff = int(witness_json["virtual_scheduled_time"]) - \
        int(witness_schedule['current_virtual_time'])
    block_diff_est = virtual_diff * virtual_time_to_block_num
    est_time_to_next_block = ''
    if active_rank > 20:
        next_block_s = int(block_diff_est) * 3
        next_block_min = next_block_s / 60
        next_block_h = next_block_min / 60
        next_block_d = next_block_h / 24
        time_diff_est = ""
        if next_block_d > 1:
            time_diff_est = "%.2f days" % next_block_d
        elif next_block_h > 1:
            time_diff_est = "%.2f hours" % next_block_h
        elif next_block_min > 1:
            time_diff_est = "%.2f minutes" % next_block_min
        else:
            time_diff_est = "%.2f seconds" % next_block_s
        est_time_to_next_block = time_diff_est

    embed = make_embed(title='Hive Witness info for @%s' %
                       witnessname)
    embed.add_field(name='Running Version',
                    value=witness_json['running_version'], inline=False)
    embed.add_field(name='Missed Blocks',
                    value=witness_json['total_missed'], inline=False)

    if est_time_to_next_block:
        embed.add_field(name='Estimate time to next block',
                        value=est_time_to_next_block, inline=False)

    if found:
        embed.add_field(name='Rank', value='%d' % rank, inline=False)
        embed.add_field(name='Active Rank', value='%d' %
                        active_rank, inline=False)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="hewitness", description="Print Hive-Engine Witness Info.")
@app_commands.describe(
    witnessname="Name of Hive-Engine witness"
)
async def hewitness(ctx: discord.Interaction, witnessname: str = 'pizza-engine'):
    """<witness name>: Print Hive-Engine Witness Info."""
    results = get_hiveengine_instance().find(
        'witnesses', 'witnesses', query={})

    results = sorted(results, key=lambda a: float(
        a['approvalWeight']['$numberDecimal']), reverse=True)

    embed = make_embed(title='Hive-Engine Witness info for @%s' %
                       witnessname)

    if len(results) == 0:
        embed.add_field(name='Hive-Engine Witness %s' %
                        witnessname, value='Not Found')
    else:
        for result in results:  # = results[0]
            if result['account'] != witnessname:
                continue

            embed.add_field(name='Rank', value=results.index(
                result) + 1, inline=True)
            result['approvalWeight'] = result['approvalWeight']['$numberDecimal']

            for key in result.keys():
                if key not in ['_id', 'signingKey', 'IP', 'RPCPort', 'P2PPort']:
                    embed.add_field(name=key, value=result[key], inline=True)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="pools", description="Check Hive-Engine DIESEL Pool Balances for Wallet.")
@app_commands.describe(
    wallet="Hive wallet name, i.e. hive.pizza."
)
async def pools(ctx: discord.Interaction, wallet: str):
    """<wallet>: Check Hive-Engine DIESEL Pool Balances for Wallet."""
    results = get_hiveengine_instance().find(
        'marketpools', 'liquidityPositions',
        query={"account": "%s" % wallet})
    embed = make_embed(title='DIESEL Pool info for @%s' % wallet)

    for result in results:
        embed.add_field(name=result['tokenPair'], value='%0.3f shares' % float(
            result['shares']), inline=True)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="pool", description="Check Hive-Engine DIESEL Pool Info.")
@app_commands.describe(
    pool="Pool symbol pair, i.e. SWAP.HIVE:PIZZA"
)
async def pool(ctx: discord.Interaction, pool: str = DEFAULT_DIESEL_POOL):
    """<pool>: Check Hive-Engine DIESEL Pool Info."""
    pool = pool.upper()

    results = get_hiveengine_instance().find(
        'marketpools', 'pools',
        query={"tokenPair": {"$in": ["%s" % pool]}})

    embed = make_embed(title='DIESEL Pool info for %s' % pool)

    if len(results) == 0:
        embed.add_field(name='DIESEL Pool %s' % pool, value='Not Found')
    else:
        result = results[0]
        for key in result.keys():
            if key not in ['_id', 'precision', 'creator']:
                embed.add_field(name=key, value=result[key], inline=True)

        results = get_hiveengine_instance().find(
            'marketpools', 'liquidityPositions',
            query={"tokenPair": {"$in": ["%s" % pool]}})
        results = sorted(results, key=lambda a: float(
            a['shares']), reverse=True)[0:13]
        for result in results:
            embed.add_field(name='LP: %s' % result['account'], value='%0.3f shares' % float(
                result['shares']), inline=True)
        embed.add_field(name='LP: ...', value='... shares', inline=True)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="poolrewards", description="Check Hive-Engine DIESEL Pool Rewards Info.")
@app_commands.describe(
    pool="Pool symbol pair, i.e. SWAP.HIVE:PIZZA"
)
async def poolrewards(ctx: discord.Interaction, pool: str = DEFAULT_DIESEL_POOL):
    """<pool>: Check Hive-Engine DIESEL Pool Rewards Info."""
    pool = pool.upper()

    query = {
        "tokenPair": {
            "$in": ["%s" % pool]
        }
    }

    results = get_hiveengine_instance().find('distribution', 'batches', query=query)

    embed = make_embed(title='DIESEL Pool Rewards for %s' % pool)

    if len(results) == 0:
        embed.add_field(name='DIESEL Pool %s' % pool, value='Not Found')
    else:
        result = results[0]

        embed.add_field(name='Payouts', value=result['numTicks'], inline=True)
        embed.add_field(name='Payouts Remaining',
                        value=result['numTicksLeft'], inline=True)

        embed.add_field(name='Last Payout Time', value='%s' %
                        datetime.fromtimestamp(result['lastTickTime'] / 1000))

        tokens = result['tokenBalances']
        for token in tokens:
            embed.add_field(name=token['symbol'], value='%0.3f' % float(
                token['quantity']), inline=True)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="buybook", description="Check Hive-Engine buy book for token.")
@app_commands.describe(
    symbol="Hive-Engine token symbol. i.e. PIZZA."
)
async def buybook(ctx: discord.Interaction, symbol: str = ''):
    """<symbol>: Check Hive-Engine buy book for token."""
    if not symbol:
        symbol = determine_native_token(ctx, DEFAULT_TOKEN_NAME)

    try:
        buy_book = get_hiveengine_market_instance().get_buy_book(symbol=symbol, limit=1000)
    except hiveengine.exceptions.TokenDoesNotExists:
        await ctx.response.send_message('Error: the Hive-Engine token symbol does not exist.')
        return

    buy_book = sorted(buy_book, key=lambda a: float(a['price']), reverse=True)
    buy_book = buy_book[0:10]

    embed = make_embed(title='Buy Book for $%s (first 10 orders)' %
                       symbol.upper())

    for row in buy_book:
        embed.add_field(value=row['account'], name='%0.3f @ %0.3f HIVE' %
                        (float(row['quantity']), float(row['price'])), inline=False)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="sellbook", description="Check Hive-Engine sell book for token.")
@app_commands.describe(
    symbol="Hive-Engine token symbol. i.e. PIZZA."
)
async def sellbook(ctx: discord.Interaction, symbol: str = ''):
    """<symbol>: Check Hive-Engine sell book for token."""
    if not symbol:
        symbol = determine_native_token(ctx, DEFAULT_TOKEN_NAME)

    try:
        sell_book = get_hiveengine_market_instance().get_sell_book(symbol=symbol, limit=1000)
    except hiveengine.exceptions.TokenDoesNotExists:
        await ctx.response.send_message('Error: the Hive-Engine token symbol does not exist.')
        return

    sell_book = sorted(sell_book, key=lambda a: float(
        a['price']), reverse=False)
    sell_book = sell_book[0:10]

    embed = make_embed(title='Sell Book for $%s (first 10 orders)' %
                       symbol.upper())

    for row in sell_book:
        embed.add_field(value=row['account'], name='%0.3f @ %0.3f HIVE' %
                        (float(row['quantity']), float(row['price'])), inline=False)

    await ctx.response.send_message(embed=embed)

# Splinterlands related helper functions and commands


@bot.tree.command(name="slplayer", description="Fetch Splinterlands info for player.")
@app_commands.describe(
    player="Name of player, status, timer."
)
async def sl(ctx: discord.Interaction, player: str):
    profile = requests.get(
        'https://api2.splinterlands.com/players/details',
        params={'name': player},
        timeout=10,
    ).json()

    embed = make_embed(title='Splinterlands profile for %s:' %
                       player)

    for k in profile.keys():
        if len(embed.fields) >= 25:
            break

        if k not in ['guild', 'display_name', 'season_details', 'adv_msg_sent']:
            prettyname = k.replace('_', ' ').title()
            if len(prettyname) > 25:
                prettyname = prettyname[:22] + '..'
            prettyvalue = str(profile[k])
            if len(prettyvalue) > 25:
                prettyvalue = prettyvalue[:22] + '..'

            embed.add_field(name=prettyname, value=prettyvalue, inline=True)

    await ctx.response.send_message(embed=embed)

# Exode related commands


@bot.tree.command(name="exodecards", description="Get a player's Exode card collection info.")
@app_commands.describe(
    player="Name of player, i.e. thebeardflex."
)
async def exodecards(ctx: discord.Interaction, player: str):
    """<player>: Get a player's Exode card collection info."""
    base_url = 'https://digitalself.io/api_feed/exode/my_delivery_api.php'
    cards = requests.get(
        base_url, params={'account': player, 'filter': 'singleCards'}, timeout=10,
    ).json()['elements']
    market_prices = [card['market_price'] for card in cards]

    elite_cards = [card for card in cards if card['is_elite']]

    packs = requests.get(
        base_url, params={'account': player, 'filter': 'packs'}, timeout=10,
    ).json()['elements']
    pack_market_prices = [pack['market_price'] for pack in packs]

    embed = make_embed(title='Exode cards for %s:' % player)
    embed.add_field(name='Card count', value=len(cards), inline=True)
    embed.add_field(name='Elite card count',
                    value=len(elite_cards), inline=True)
    embed.add_field(name='Packs count', value=len(packs), inline=True)
    embed.add_field(name='Total market value', value='$%0.3f' %
                    (sum(market_prices) + sum(pack_market_prices)), inline=True)

    await ctx.response.send_message(embed=embed)


# Rising Star related commands
@bot.tree.command(name="rsplayer", description="Check Rising Star Player Stats.")
@app_commands.describe(
    player="Name of player, i.e. thebeardflex."
)
async def rsplayer(ctx: discord.Interaction, player: str):
    """<player>: Check Rising Star Player Stats."""
    try:
        profile = requests.get(
            'https://www.risingstargame.com/playerstats.asp',
            params={'player': player},
            timeout=10,
        ).json()[0]
    except json_lib.decoder.JSONDecodeError:
        await ctx.response.send_message('Error: unable to fetch risingstar data.')
        return

    embed = make_embed(title='Rising Star Profile for @%s' %
                       player)

    for k in profile.keys():
        if k not in ['name']:
            prettyname = k.title()
            if prettyname == 'Missionego':
                prettyname = 'Mission Ego'
            elif prettyname == 'Lessonskill':
                prettyname = 'Lesson Skill'
            elif prettyname == 'Totalnfts':
                prettyname = 'Total NFTs'
            elif prettyname == 'Cardsfans':
                prettyname = 'Cards Fans'
            elif prettyname == 'Cardskill':
                prettyname = 'Cards Skill'
            elif prettyname == 'Cardsluck':
                prettyname = 'Cards Luck'
            elif prettyname == 'Cardsim':
                prettyname = 'Cards Income'

            embed.add_field(name=prettyname, value=profile[k], inline=True)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="links", description="Use these links to support Hive.Pizza.")
async def links(ctx: discord.Interaction):
    """Use these links to support Hive.Pizza."""
    embed = make_embed(
        title='Hive.Pizza links',
        description='Please consider supporting Hive.Pizza '
                    'by using these referral links.')
    embed.add_field(name='Hive Signup (1)',
                    value='https://hive.pizza/hiveonboard', inline=False)
    embed.add_field(name='Hive Signup (2)',
                    value='https://hive.pizza/ecency', inline=False)
    embed.add_field(
        name='dCrops', value='https://hive.pizza/dcrops', inline=False)
    embed.add_field(
        name='Exode', value='https://hive.pizza/exode', inline=False)
    embed.add_field(name='NFTShowroom',
                    value='https://hive.pizza/nftshowroom', inline=False)
    embed.add_field(name='Rising Star',
                    value='https://hive.pizza/risingstar', inline=False)
    embed.add_field(name='Splinterlands',
                    value='https://hive.pizza/splinterlands', inline=False)
    embed.add_field(name='Terracore',
                    value='https://hive.pizza/terracore', inline=False)

    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="rc", description="Show Hive resource credits status for wallet.")
@app_commands.describe(
    wallet="name of wallet"
)
async def rc(ctx: commands.Context, wallet: str):
    """Print Hive resource credits info for wallet."""
    rc = beem.rc.RC(hive_instance=get_hive_instance())
    comment_cost = rc.comment()
    vote_cost = rc.vote()
    json_cost = rc.custom_json()
    account_cost = rc.claim_account()

    acc = beem.account.Account(wallet, blockchain_instance=get_hive_instance())
    mana = acc.get_rc_manabar()['current_mana']

    possible_jsons = int(mana / json_cost)
    possible_votes = int(mana / vote_cost)
    possible_comments = int(mana / comment_cost)
    possible_accounts = int(mana / account_cost)

    current_pct = float(acc.get_rc_manabar()['current_pct'])
    embed = make_embed(
        title='Hive Resource Credits for @%s' % wallet,
        description='RC manabar is at %0.3f%%' % current_pct)
    embed.add_field(name='Account Claims ', value='~ %d' %
                    possible_accounts, inline=True)
    embed.add_field(name='Comments/Posts', value='~ %d' %
                    possible_comments, inline=True)
    embed.add_field(name='Votes', value='~ %d' % possible_votes, inline=True)
    embed.add_field(name='CustomJSONs', value='~ %d' %
                    possible_jsons, inline=True)
    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="status", description="Print bot's status information.")
async def status(ctx: discord.Interaction):
    """Print bot's status information."""

    accounts = ['pizza.witness', 'pizza-engine']
    accounts += ['pizza-dlux', 'pizza-rewards', 'hive.pizza', 'pizzabot']
    accounts += ['badge-912244']

    embed = make_embed(
        title='Hive Pizza Systems Status',
        description='PizzaNet Systems are Operational. '
                    ':green_circle:')

    embed.add_field(name=bot.user, value='Serving %d Discord guilds.\n' % (
        len(bot.guilds)), inline=False)

    for account in accounts:
        acc = beem.account.Account(account, blockchain_instance=get_hive_instance())
        current_pct = float(acc.get_rc_manabar()['current_pct'])

        extra_info = ''

        if account == 'pizza.witness':
            active_rank = 0
            witnesses = WitnessesRankedByVote(
                limit=101, blockchain_instance=get_hive_instance())
            for w in witnesses:
                if w.is_active:
                    active_rank += 1
                if w["owner"] == account:
                    break

            extra_info = ' | Active Rank %d' % active_rank

        if account == 'pizza-engine':
            # get HE witness rank
            results = get_hiveengine_instance().find('witnesses', 'witnesses', query={})
            results = sorted(results, key=lambda a: float(
                a['approvalWeight']['$numberDecimal']), reverse=True)
            for result in results:  # = results[0]
                if result['account'] != 'pizza-engine':
                    continue
                he_witness_rank = results.index(result) + 1
                extra_info = ' | Rank %d' % he_witness_rank

        embed.add_field(name=account, value=':battery: %d%%%s' %
                        (current_pct, extra_info), inline=True)

    await ctx.response.send_message(embed=embed)

# Hive Content Commands


@bot.tree.command(name="blog", description="Link to latest post from blog.")
@app_commands.describe(
    name="Hive blog name, i.e. hive.pizza."
)
async def blog(ctx: discord.Interaction, name: str):
    """<name> : Link to last post from blog."""
    account = beem.account.Account(name)
    latest_blog = account.get_blog(0, 1)[0]

    if not latest_blog:
        response = 'Blog not found'
    else:
        reply_identifier = '@%s/%s' % (
            latest_blog['author'], latest_blog['permlink'])
        response = 'Latest post from @%s: https://peakd.com/%s' % (
            name, reply_identifier)

    await ctx.response.send_message(response)


@bot.tree.command(name="search", description="Search for Hive content.")
@app_commands.describe(
    query="Search query",
    sort="How to filter search results."
)
async def search(ctx: discord.Interaction, query: str, sort: str = 'relevance'):
    """Search for Hive content."""
    HIVESEARCHER_URL = 'https://api.hivesearcher.com/search'
    cfg = load_config()

    headers = {'Authorization': cfg.hivesearcher_api_key}

    response = requests.post(
        HIVESEARCHER_URL,
        json={"q": query, "sort": sort},
        headers=headers,
        timeout=10,
    ).json()
    results = response['results']

    embed = make_embed(
        title='Hive Content Search Results from HiveSearcher',
        description='Showing 10 results for %s, sorted by %s\n'
                    % (query, sort))
    for result in results[0:10]:
        if result['title']:
            message = 'by %s. <https://peakd.com/@%s/%s>\n' % (
                result['author'], result['author'], result['permlink'])
            embed.add_field(name='%d. %s' % (results.index(
                result), result['title']), value=message, inline=False)
        else:
            message = 'by %s. <https://peakd.com/@%s/%s>\n' % (
                result['author'], result['author'], result['permlink'])
            embed.add_field(name='%d. %s' % (results.index(
                result), 'Comment'), value=message, inline=False)

    await ctx.response.send_message(embed=embed)


@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1
    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle unhandled slash command errors."""
    try:
        if interaction.response.is_done():
            await interaction.followup.send("An error occurred. Please try again later.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred. Please try again later.", ephemeral=True)
    except discord.HTTPException:
        pass
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@bot.event
async def on_command_error(ctx: discord.Interaction, error: Exception):
    """Print out exception for debugging."""
    if isinstance(error, commands.CommandNotFound):
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


@bot.event
async def on_ready():
    """Event handler for bot comnnection."""
    logger.info('%s has connected to Discord!', bot.user)
    logger.info('Serving %d Discord guilds.', len(bot.guilds))
    await update_bot_user_status(bot)

    PizzaCog(bot)

    # bot.tree.clear_commands(guild=None, type=None)
    # await bot.tree.sync()
    # await bot.tree.sync(guild=None)

    await bot.tree.sync(guild=None)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
    cfg = load_config()
    bot.run(cfg.discord_token)
