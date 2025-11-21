#!/usr/bin/env python3
"""Discord bot for Hive Pizza community."""
import beem
from beem.witness import Witness, WitnessesRankedByVote
import datetime
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands, tasks
import hiveengine
from hiveengine.api import Api
from hiveengine.market import Market
from hiveengine.tokenobject import Token
from hiveengine.wallet import Wallet
import json
import os
from dotenv import load_dotenv
import random

import requests
import sys
import traceback

from typing import Literal, Optional


from utils import *
from utils_hiveengine import *
from utils_hive import *

# Hive-Engine defines
hive = get_hive_instance()

load_dotenv()
HIVE_ENGINE_API_NODE = os.getenv('HIVE_ENGINE_API_NODE')
HIVE_ENGINE_API_NODE_RPC = os.getenv('HIVE_ENGINE_API_NODE_RPC')
hiveengine_api = Api(url=HIVE_ENGINE_API_NODE, rpcurl=HIVE_ENGINE_API_NODE_RPC)
market = Market(api=hiveengine_api, blockchain_instance=hive)

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
            wallet, blockchain_instance=hive, api=hiveengine_api).get_token(symbol)

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

    embed = discord.Embed(title='Balances for @%s' %
                          wallet, description='$%s' % symbol, color=0x336EFF)
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
            wallet, blockchain_instance=hive, api=hiveengine_api)
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

    embed = discord.Embed(title='First 10 balances for @%s' %
                          wallet, description=message_body, color=0x90be6d)
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

    # TODO : add all text command gif options to the slash command definition

    PIZZA_GIFS = ['https://tenor.com/bOpfE.gif', 'https://tenor.com/bOphp.gif', 'https://tenor.com/bOpms.gif', 'https://tenor.com/bLZrj.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930920031561330688/hp_shuffle.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930606139941453864/Matrix_Morpheus_offeringPizza_logo.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930565316218601502/hp_therock.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930430486294171668/hp_sono.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930430485786656798/hp_snoop1.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930430484717129768/hp_rocketlaunch.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930430483957940254/hp_raindance.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930430483492401152/hp_nom.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/930276777920712714/slama.gif',
                  'https://media.giphy.com/media/IzfbNtUU4MMw1PL1qV/giphy-downsized-large.gif', 'https://media.giphy.com/media/EkOibKD5yUa0tgLCxN/giphy.gif', 'https://media.giphy.com/media/5yn8SyAzwUBEgdALRa/giphy-downsized-large.gif', 'https://media.giphy.com/media/TrsWfYuKTRd1jAJrcH/giphy.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/929578506847932416/20220108_222854.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/929574678475976725/final_61da51208515290112872774_913648.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/929565611271520286/20220108_214058.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/929563942097944576/final_61da4461b9c9760065a7e297_963344.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/929558244890931220/When_you_rank_up_in_PIZZA.gif', 'https://cdn.discordapp.com/attachments/929541976553037824/929556529391206501/final_61da3f1d855e34006355ecd7_133726.gif']
    PINEAPPLE_GIFS = ['https://media.giphy.com/media/0gYYWq5dHfhnYVrYtI/giphy.gif', 'https://media.giphy.com/media/7gXkay4o8FnFzT7uJo/giphy.gif', 'https://media.giphy.com/media/pz4hZwrBZn4EGxpMlG/giphy.gif', 'https://media.giphy.com/media/ZDgaXZjeKWnzuf5RRF/giphy.gif', 'https://media.giphy.com/media/vxyDfIe3iRXhsJ7z5r/giphy.gif', 'https://media.giphy.com/media/Ganp5Ne5MdzkdupCRF/giphy.gif', 'https://media.giphy.com/media/tIxf5oMxG1PWUYJEcL/giphy.gif', 'https://media.giphy.com/media/JG2ziQmGrc0MrHzGuj/giphy.gif', 'https://media.giphy.com/media/uVW9moVaAR47Vgj7D0/giphy.gif', 'https://media.giphy.com/media/rHLj0lWywWuaeGiSTF/giphy.gif', 'https://media.giphy.com/media/XCvm5Oo6wEVJmxRx7V/giphy.gif', 'https://media.giphy.com/media/7b6sSJEEBqWatW2MYn/giphy.gif',
                      'https://media.giphy.com/media/18odCx2irVLDrvO3fY/giphy.gif', 'https://media.giphy.com/media/3g23LxFceQW8poMpTs/giphy.gif', 'https://media.giphy.com/media/N1ZxRLeX5wIz9Tvs8X/giphy.gif', 'https://media.giphy.com/media/ZwPHgEzoTcyKtaIlId/giphy.gif', 'https://media.giphy.com/media/9FmzQEdSbuSXcsPXCT/giphy.gif', 'https://media.giphy.com/media/WFdZOAE8OYcq5tSXee/giphy.gif', 'https://media.giphy.com/media/Bns85ZwsExoGgsKMmK/giphy.gif', 'https://media.giphy.com/media/Caoow9v9MRNIqmoFJJ/giphy.gif', 'https://media.giphy.com/media/3rTPQ1jH5osS4aBX8D/giphy.gif', 'https://media.giphy.com/media/FAqmU08XQKcGzzTpwO/giphy.gif', 'https://media.giphy.com/media/mQnBlO24UTPN723dpe/giphy.gif', 'https://media.giphy.com/media/RGV125iyT97ONLweyx/giphy.gif', 'https://media.giphy.com/media/vH5awikXqtANyuob7T/giphy.gif']
    BRO_GIFS = ['https://media.giphy.com/media/Q7dRGcu38WqGnb7nnI/giphy.gif', 'https://media.giphy.com/media/V9RSXFgeldCNKLCydK/giphy.gif', 'https://media.giphy.com/media/jSKXXzMxL55JUN93Q6/giphy.gif', 'https://media.giphy.com/media/XKXP9qdvV14N445Im4/giphy.gif', 'https://media.giphy.com/media/GaySGYuvjk2u2ql7XU/giphy.gif', 'https://media.giphy.com/media/tUgNHh1rupdbZ30mrP/giphy.gif', 'https://media.giphy.com/media/41bHp9qHeO9G2RKKFs/giphy.gif', 'https://media.giphy.com/media/PVRn0PcZ1las7eow4J/giphy.gif', 'https://media.giphy.com/media/7gZ7c3LJZ9Z8l85EtY/giphy.gif', 'https://media.giphy.com/media/v8jgENvvlegjuxLOmc/giphy.gif', 'https://media.giphy.com/media/tbYfDQ8fX8siY80sBN/giphy.gif', 'https://media.giphy.com/media/WFHauwzA2gcVhXxMuH/giphy.gif',
                'https://media.giphy.com/media/65yRhgpIYVcB8SICtF/giphy.gif', 'https://media.giphy.com/media/mkN81kU4YqteLCqPvU/giphy.gif', 'https://media.giphy.com/media/o6Dfmyj2p4S5a3oxz6/giphy.gif', 'https://media.giphy.com/media/A66FeQBsflVqikTe3m/giphy.gif', 'https://media.giphy.com/media/EDCIaFhFaAYsdkbwgd/giphy.gif', 'https://media.giphy.com/media/rGh7YlCLOkqlyOFpq9/giphy.gif', 'https://media.giphy.com/media/v32eWRX8XE8Vh2l44h/giphy.gif', 'https://media.giphy.com/media/6nVXn29SXPMHiPKgXi/giphy.gif', 'https://media.giphy.com/media/w67kdyKjyNr2Xeb3fM/giphy.gif', 'https://media.giphy.com/media/piNBUyg9b7yAFSexql/giphy.gif', 'https://media.giphy.com/media/umiHQSmGsF5EiVSAv6/giphy.gif', 'https://media.giphy.com/media/CyKE41GQ2srFBIHTiL/giphy.gif', 'https://media.giphy.com/media/9fnjcqc49X3uqjlZra/giphy.gif']
    RISINGSTAR_GIFS = ['https://media.giphy.com/media/4fKFmbMTl2guk1n6y2/giphy.gif', 'https://media.giphy.com/media/T9QH5wAUPT8o2trbjD/giphy.gif', 'https://media.giphy.com/media/gL8iKEDRWzCdl6nk5G/giphy.gif', 'https://media.giphy.com/media/NchY6QQ2hzQisINQjA/giphy.gif', 'https://media.giphy.com/media/EkVBC57QI4U9IQfkY2/giphy.gif', 'https://media.giphy.com/media/IVYphXkTnL7EXn0gs3/giphy.gif', 'https://media.giphy.com/media/zj2H8HhLVtWnuGYqhx/giphy.gif', 'https://media.giphy.com/media/LDQqkkB1nhIr1kFsu7/giphy.gif', 'https://media.giphy.com/media/yHc7yfgyXRhLa5Q0qJ/giphy.gif', 'https://media.giphy.com/media/uYxnx1eiuhW97JvOAi/giphy.gif', 'https://media.giphy.com/media/jTTZ6zIsbcuRLisxLb/giphy.gif', 'https://media.giphy.com/media/Um2rquzMWZKQUbpT0I/giphy.gif',
                       'https://media.giphy.com/media/iH7FY0ukmmetUZHT0K/giphy.gif', 'https://media.giphy.com/media/rJ6tKAaV0IkvjH0ys4/giphy.gif', 'https://media.giphy.com/media/LUKMkHzmJkaCkpvHVg/giphy.gif', 'https://media.giphy.com/media/6YFeS3ejyheLd96ibx/giphy.gif', 'https://media.giphy.com/media/9zjksORdGKFecNYjUk/giphy.gif', 'https://media.giphy.com/media/Gk1Ch0WHuqknkBjLIn/giphy.gif', 'https://media.giphy.com/media/MjOvM7AdJDtKBKckJT/giphy.gif', 'https://media.giphy.com/media/i5XGW0zW6prU3L0WRM/giphy.gif', 'https://media.giphy.com/media/uYX7r0u449s49oWFLY/giphy.gif', 'https://media.giphy.com/media/QU0uxCUe6qVmwoLErs/giphy.gif', 'https://media.giphy.com/media/DSwdsnBw1qbLfL4NaB/giphy.gif', 'https://media.giphy.com/media/BY2W5iI5TrqVbC3eYo/giphy.gif', 'https://media.giphy.com/media/6kzDBcHoWzcwTbSSU8/giphy.gif']
    POB_GIFS = ['https://media.giphy.com/media/btd5gT1uEKVUrMTM5F/giphy.gif', 'https://media.giphy.com/media/EPNH2hv2BTNm0c0i40/giphy.gif', 'https://media.giphy.com/media/t05mKJb8YiLlgckcC3/giphy.gif', 'https://media.giphy.com/media/q8K77RTBUmaSaWFgrE/giphy.gif', 'https://media.giphy.com/media/L6jEwgKyftQmSTJevb/giphy.gif', 'https://media.giphy.com/media/IioSnIxFIFed93The1/giphy.gif', 'https://media.giphy.com/media/VdQgGCxoc4gF3L4zY3/giphy.gif', 'https://media.giphy.com/media/Dou0bMmL4pxFem0zH0/giphy.gif',
                'https://media.giphy.com/media/PmtcPpxG7o5PqM7YX4/giphy.gif', 'https://media.giphy.com/media/7Vqr9VKanN29Q1rbgr/giphy.gif', 'https://media.giphy.com/media/KZXlJ4K6Lr9INnvkUQ/giphy.gif', 'https://media.giphy.com/media/DGto0zMPaXIRkkHtMn/giphy.gif', 'https://media.giphy.com/media/9RulVBzWtHwz8AYmHw/giphy.gif', 'https://media.giphy.com/media/HHzLyXlf1HDhB2FAK6/giphy.gif', 'https://media.giphy.com/media/HD1cOJ7vltQtPoOyJM/giphy.gif', 'https://media.giphy.com/media/wiGC2mE3nM3hD8kinf/giphy.gif', 'https://media.giphy.com/media/BqoMcPD1vfDc55bUtK/giphy.gif']
    PROFOUND_GIFS = ['https://media.giphy.com/media/SQ5M4nABcnPsRv4Sux/giphy.gif', 'https://media.giphy.com/media/6ar045QB2RuxeZfb6U/giphy.gif', 'https://media.giphy.com/media/L6xgc2dWJHb3eks3xa/giphy.gif', 'https://media.giphy.com/media/f2edaKKz4SWW6b60v2/giphy.gif', 'https://media.giphy.com/media/LNSWLRhRnjGX0d4Xqc/giphy.gif', 'https://media.giphy.com/media/QUpkbYcHGqxsKuGv5D/giphy.gif', 'https://media.giphy.com/media/XJmwDVhGnkjrmonuny/giphy.gif', 'https://media.giphy.com/media/NGNW6ZR2bV3C66LvnM/giphy.gif', 'https://media.giphy.com/media/zutsNVWa5PnmWLLORT/giphy.gif', 'https://media.giphy.com/media/2P4Ov6WtnxU4iFPx0C/giphy.gif', 'https://media.giphy.com/media/i6Qepo5EKDuruePSvV/giphy.gif', 'https://media.giphy.com/media/nDMbce12xS59Fh0oN2/giphy.gif',
                     'https://media.giphy.com/media/8G6N3UPP2FNLh3zJB9/giphy.gif', 'https://media.giphy.com/media/bIAm0uWiz2jZANh9at/giphy.gif', 'https://media.giphy.com/media/EYkkdDgnir7EcV61CJ/giphy.gif', 'https://media.giphy.com/media/nFkyu4FFGIlFZrt5n8/giphy.gif', 'https://media.giphy.com/media/0UkEoh2xT59QDTTF70/giphy.gif', 'https://media.giphy.com/media/7jGdJCHDBffOOSyxlf/giphy.gif', 'https://media.giphy.com/media/f64GgzL3cnF3WhuPjb/giphy.gif', 'https://media.giphy.com/media/RzUct7rduOf4976qjP/giphy.gif', 'https://media.giphy.com/media/yvQiEvCmDsjQe0BFJi/giphy.gif', 'https://media.giphy.com/media/3Nmzke5aDoj23Cu1AL/giphy.gif', 'https://media.giphy.com/media/dln8uROMLJylGIaHnZ/giphy.gif', 'https://media.giphy.com/media/19HdKao5FdOXwLowu5/giphy.gif', 'https://media.giphy.com/media/bNk3MLtmKaSSgGvqUe/giphy.gif']
    BATTLEAXE_GIFS = ['https://media.giphy.com/media/8Oup5mUGVs2dZWNhCw/giphy.gif', 'https://media.giphy.com/media/twrPnIhjarlfVqhTvt/giphy.gif', 'https://media.giphy.com/media/aGaoKokoF4F7rFhb3a/giphy.gif', 'https://media.giphy.com/media/oDtC2KVOy9HNcG4y8s/giphy.gif', 'https://media.giphy.com/media/7U115amErU5M7Zuk6k/giphy.gif', 'https://media.giphy.com/media/aW2x62TDaNcwzLFT3L/giphy.gif',
                      'https://media.giphy.com/media/CRg4wEkzJRQ8ljNbUK/giphy.gif', 'https://media.giphy.com/media/AobPC1jh48luCFEREk/giphy.gif', 'https://media.giphy.com/media/p8hrL9PQq6S3JS6Z9w/giphy.gif', 'https://media.giphy.com/media/AJ82ifdfuN7D9OVDOv/giphy.gif', 'https://media.giphy.com/media/HbiFp4eWszvZdt2nr0/giphy.gif', 'https://media.giphy.com/media/jWAgAxHUxkeXxD4l4H/giphy.gif', 'https://media.giphy.com/media/33QVGxmaiL87VpNQJg/giphy.gif']
    ENGLAND_GIFS = ['https://media.giphy.com/media/u9a7I1NjCRwDJvgQBe/giphy.gif', 'https://media.giphy.com/media/QCAwYlATLHAJZYyjId/giphy.gif', 'https://media.giphy.com/media/f71WnctzJj20XpXwrq/giphy.gif', 'https://media.giphy.com/media/5X7JrKbLgyYAIGcJrv/giphy.gif', 'https://media.giphy.com/media/hA88d22fB2ik0OoYsk/giphy.gif',
                    'https://media.giphy.com/media/VdcUMBoJBIxWNCjZFH/giphy.gif', 'https://media.giphy.com/media/VGXIQEXKWRNtmwR3ar/giphy.gif', 'https://media.giphy.com/media/H6b0VeNQLKaeziLOZ5/giphy.gif', 'https://media.giphy.com/media/5qwy92o8UyRm1p1KFe/giphy.gif', 'https://media.giphy.com/media/QhcLXkIxm8I0cgANr0/giphy.gif']
    HUZZAH_GIFS = ['https://media.giphy.com/media/NK7s1mf7kyqvdhpPda/giphy.gif', 'https://media.giphy.com/media/cutDOWJ6TFOcPGNzbh/giphy.gif', 'https://media.giphy.com/media/qnGXaSWrBAu2z81Izt/giphy.gif', 'https://media.giphy.com/media/UGo7mKoHRPf1QB4TjE/giphy.gif', 'https://media.giphy.com/media/BbqkuiiJRbXGrbB3ia/giphy.gif', 'https://media.giphy.com/media/PxpcFRl7xzgaBsKauK/giphy.gif', 'https://media.giphy.com/media/WTYXq0mkUdzKBsoMhO/giphy.gif', 'https://media.giphy.com/media/GjQvNDr1Q5BaKQLxjY/giphy.gif',
                   'https://media.giphy.com/media/NeCZITVgP6C7xSCGql/giphy.gif', 'https://media.giphy.com/media/eEcRLf42mV9NalRqoU/giphy.gif', 'https://media.giphy.com/media/YpJyG2HsU5wZfZ6il0/giphy.gif', 'https://media.giphy.com/media/Gz8XfN6Uf7p4ISuhyk/giphy.gif', 'https://media.giphy.com/media/anBYsqSFAVKK7nbVFT/giphy.gif', 'https://media.giphy.com/media/XOnavX6DuHgVAxcszH/giphy.gif', 'https://media.giphy.com/media/JHbGALEbQFGMpAje0F/giphy.gif', 'https://media.giphy.com/media/pUxGNcUp2UipqVUxcZ/giphy.gif', 'https://media.giphy.com/media/x7ILoVXOJ2VM8UBBR5/giphy.gif']
    BEARD_GIFS = ['https://media.giphy.com/media/GDGgyNaADzlfgFxsQ8/giphy.gif', 'https://media.giphy.com/media/vGNnl2zd7bWGhtux3l/giphy.gif', 'https://media.giphy.com/media/7eTqcO2RRq74IHHwub/giphy.gif', 'https://media.giphy.com/media/K40oW5YgCjBD4GnTAX/giphy.gif', 'https://media.giphy.com/media/hpQ8rTRaN84jTaKQIV/giphy.gif', 'https://media.giphy.com/media/y6uXquI7zySNQaguo7/giphy.gif', 'https://media.giphy.com/media/kW7SpyVapoeolLhHaV/giphy.gif', 'https://media.giphy.com/media/rLnsxjSUvArSrOfRDO/giphy.gif', 'https://media.giphy.com/media/iSsOEvgcXsBgJ0Tvt6/giphy.gif', 'https://media.giphy.com/media/UCLddjtFovvUzAsOYM/giphy.gif',
                  'https://media.giphy.com/media/j54tWqI1SyLlbkFB8v/giphy.gif', 'https://media.giphy.com/media/lWNCmxhRAtgDGDG80t/giphy.gif', 'https://media.giphy.com/media/hiZyT60Y6DcpNIu2IG/giphy.gif', 'https://media.giphy.com/media/YGxkIWgTeoMO2a8gVL/giphy.gif', 'https://media.giphy.com/media/UdvdbCu1efca3ZjbYZ/giphy.gif', 'https://media.giphy.com/media/J1bWno6ecjcenHEYoh/giphy.gif', 'https://media.giphy.com/media/tjFdjyJvH7jhW1b3Fr/giphy.gif', 'https://media.giphy.com/media/DsXgYmws370VALFG24/giphy.gif', 'https://media.giphy.com/media/R6sF4SGktcZkirUeMP/giphy.gif', 'https://media.giphy.com/media/LRZOlgqsKZuufctGJQ/giphy.gif']
    LEGO_GIFS = ['https://media.giphy.com/media/G4kwvrvmlt8ciKjXP9/giphy.gif', 'https://media.giphy.com/media/h0tq5gDYnlOIJqvIfF/giphy.gif', 'https://media.giphy.com/media/mxjWb3yvsHUL4GMTst/giphy.gif', 'https://media.giphy.com/media/ImgQcjJ03oLToYZJWn/giphy.gif', 'https://media.giphy.com/media/EU1IkLvFtXXvx5qAVw/giphy.gif', 'https://media.giphy.com/media/uxMzxj8lK1FjruVaYo/giphy.gif', 'https://media.giphy.com/media/zgsuashHk2AH3kT0rj/giphy.gif', 'https://media.giphy.com/media/Pf9LofhYG1LTOHlziK/giphy.gif', 'https://media.giphy.com/media/FYCT2NgFyiZFzOHg8Y/giphy.gif', 'https://media.giphy.com/media/Z6RiM5gsJhlM91gybi/giphy.gif',
                 'https://media.giphy.com/media/Wj01dlce8lonswtCT3/giphy.gif', 'https://media.giphy.com/media/pbXQYjv9PaPUqil4MW/giphy.gif', 'https://media.giphy.com/media/B4wi6kDqDlZrv8NxTU/giphy.gif', 'https://media.giphy.com/media/El1P68jATWuZY6EYlQ/giphy.gif', 'https://media.giphy.com/media/DbYb1CUpnPNuZJVaNN/giphy.gif', 'https://media.giphy.com/media/dPpWDZk0XVRToXdZLy/giphy.gif', 'https://media.giphy.com/media/7FYC9A7LuEYf9e30na/giphy.gif', 'https://media.giphy.com/media/FhRwcmMEH9PkgjpllS/giphy.gif', 'https://media.giphy.com/media/H6rOWKlATmWnybS9mq/giphy.gif', 'https://media.giphy.com/media/NVktVqdCuzQ8dIVaVa/giphy.gif', 'https://media.giphy.com/media/CkOlg6FupoHZww9tIk/giphy.gif']
    BLURT_GIFS = ['https://media.giphy.com/media/NDiXQBhcBe3i9pdsiw/giphy.gif', 'https://media.giphy.com/media/Sda1O3NXrO3s5pKtHw/giphy.gif', 'https://media.giphy.com/media/rWRW4322Cfru0Z5eEf/giphy.gif', 'https://media.giphy.com/media/geqRxwm5vx1QB0DWCR/giphy.gif', 'https://media.giphy.com/media/jytuKu4PXw6KYmcdc8/giphy.gif', 'https://media.giphy.com/media/RQ5qYz9BGWJbPXO8H4/giphy.gif', 'https://media.giphy.com/media/RV4cxcOAG45gX7KOix/giphy.gif', 'https://media.giphy.com/media/YM5Gw9xULBqF2qumB3/giphy.gif', 'https://media.giphy.com/media/QzIeA2TVcgCUIw2E8w/giphy.gif', 'https://media.giphy.com/media/p76jXuNFEVMOk59IAo/giphy.gif',
                  'https://media.giphy.com/media/fwZoVhxb3sVxoYDbep/giphy.gif', 'https://media.giphy.com/media/So8RwXWYlRKIZDlBqC/giphy.gif', 'https://media.giphy.com/media/d8PqnnR3AD7yCyfuhA/giphy.gif', 'https://media.giphy.com/media/rhyFAc2RcmEtxGiARK/giphy.gif', 'https://media.giphy.com/media/JB7YYqDDQxzdJtwF9Q/giphy.gif', 'https://media.giphy.com/media/BOUIxbEFm4CWtW72EK/giphy.gif', 'https://media.giphy.com/media/Pt9Qe5vR0dCRDQh7H4/giphy.gif', 'https://media.giphy.com/media/ffdprDwi9tVotD7m38/giphy.gif', 'https://media.giphy.com/media/3kGxK0wO8M8BlIDCBZ/giphy.gif', 'https://media.giphy.com/media/Q41Dxo5RGLtfDCXSmV/giphy.gif', 'https://media.giphy.com/media/FsfS2UQOZKjSa8w10I/giphy.gif']
    FOXON_GIFS = ['https://media.giphy.com/media/DhKudYKoGOyJFHKA1r/giphy.gif', 'https://media.giphy.com/media/9ZNogzYmzRLHYXDtcR/giphy.gif',
                  'https://media.giphy.com/media/t3q7z5EcDmmPMwBd0i/giphy.gif', 'https://media.giphy.com/media/8imbHuhI8ZhMUQ8p0r/giphy.gif', 'https://media.giphy.com/media/BlMaitisfAtUEzKQLS/giphy.gif']
    STICKUP_GIFS = ['https://media.giphy.com/media/XjjTY8qh3fZoQq5Tdu/giphy.gif', 'https://media.giphy.com/media/RrY68snArrNqERTCgc/giphy.gif', 'https://media.giphy.com/media/GNo3xnUtqNi5OIMhsu/giphy.gif', 'https://media.giphy.com/media/E5mi11dBhuiW4fOC2c/giphy.gif', 'https://media.giphy.com/media/Mm1wJNenpnBj76BlJJ/giphy.gif', 'https://media.giphy.com/media/utx5mlMfovTsUs5F69/giphy.gif', 'https://media.giphy.com/media/VchyhdU86WbsUjVNP7/giphy.gif', 'https://media.giphy.com/media/Fd6NEw3kR6ZaMnn5sX/giphy.gif', 'https://media.giphy.com/media/JFOdcPiOiaOwXhIz4q/giphy.gif', 'https://media.giphy.com/media/DqB8cqbWW0g6GfSBwu/giphy.gif', 'https://media.giphy.com/media/79K306oJupprCsf8DU/giphy.gif', 'https://media.giphy.com/media/lEqhVHS94PIlzoZCxP/giphy.gif',
                    'https://media.giphy.com/media/fLHHHzwYx61oHKBFT9/giphy.gif', 'https://media.giphy.com/media/npsHLArWNwR9kBp9Hz/giphy.gif', 'https://media.giphy.com/media/1s8xWlUv6pwE1LacIN/giphy.gif', 'https://media.giphy.com/media/qx8ydGluxIZctEpN7x/giphy.gif', 'https://media.giphy.com/media/LTTnOl7BDBQfeyGB0B/giphy.gif', 'https://media.giphy.com/media/2pcDVqocJ7uaZHYiFI/giphy.gif', 'https://media.giphy.com/media/p8BTBEsZrtG59Dni6t/giphy.gif', 'https://media.giphy.com/media/eVBNtrAXJu3mZ7bXGF/giphy.gif', 'https://media.giphy.com/media/FSIP4YFjm2fmaiRLk9/giphy.gif', 'https://media.giphy.com/media/MywBmUQxpNEJrNEwhz/giphy.gif', 'https://media.giphy.com/media/uVjVmXIPgwIoHYHsto/giphy.gif', 'https://media.giphy.com/media/1AhvGqvRafICfhu62z/giphy.gif', 'https://media.giphy.com/media/NGadEwb2motzfaoBV7/giphy.gif']
    CINE_GIFS = ['https://media.giphy.com/media/FIyurUoMubWnaeXDbc/giphy.gif', 'https://media.giphy.com/media/6w4JmLoxAU0PCXe2xm/giphy.gif', 'https://media.giphy.com/media/CsklEOU26Chulc5Udg/giphy.gif', 'https://media.giphy.com/media/iIwLGWvsdrKInCU6pY/giphy.gif', 'https://media.giphy.com/media/YLMY3IFdMmqquCnbDw/giphy.gif', 'https://media.giphy.com/media/EIPgvGf26GHXqS34ms/giphy.gif', 'https://media.giphy.com/media/PMrgmU0eMbUbhwArsE/giphy.gif', 'https://media.giphy.com/media/l3LTdvgaMsg6hIbNQQ/giphy.gif', 'https://media.giphy.com/media/N7lrDrPZ2d6Ad1oHsV/giphy.gif', 'https://media.giphy.com/media/ersmVWkUPttGKVSstD/giphy.gif', 'https://media.giphy.com/media/wZJxb1ZGXlD6cdbNen/giphy.gif', 'https://media.giphy.com/media/qqmOLhVRrDgBS0M2rT/giphy.gif',
                 'https://media.giphy.com/media/3kgq6266FccZ2Jd2R6/giphy.gif', 'https://media.giphy.com/media/8jMIg3s65D4FpFmWZu/giphy.gif', 'https://media.giphy.com/media/7Idr5i34o3t8edcRCO/giphy.gif', 'https://media.giphy.com/media/ttWgnjl1WOIinoukq6/giphy.gif', 'https://media.giphy.com/media/hUBWNDBoBQTAXvsCQ6/giphy.gif', 'https://media.giphy.com/media/9GRzz5tUZiaJzy6rWO/giphy.gif', 'https://media.giphy.com/media/lQn6yyxsJgwhmQ0vdf/giphy.gif', 'https://media.giphy.com/media/O8qK5rGtDRDqHNC8Ec/giphy.gif', 'https://media.giphy.com/media/FHhOi6Moto68gNyafW/giphy.gif', 'https://media.giphy.com/media/Qf0udrUFdPRcgyTpp0/giphy.gif', 'https://media.giphy.com/media/RTxUucAqSFMT8xtK0Q/giphy.gif', 'https://media.giphy.com/media/FQL3zfy80vCe7OFnE2/giphy.gif', 'https://media.giphy.com/media/MuRcAxHKqeiTzEuHpC/giphy.gif']
    DIBBLERS_GIFS = ['https://media.giphy.com/media/ETDRQrFfcPKo1gvkSx/giphy.gif', 'https://media.giphy.com/media/pwTCAu1w6izTIZsqVD/giphy.gif', 'https://media.giphy.com/media/PlpMSapjUC96ywP4HI/giphy.gif',
                     'https://media.giphy.com/media/wMPFGSSEB170mttNAJ/giphy.gif', 'https://media.giphy.com/media/3armSt6Qqwul8HwmIJ/giphy.gif', 'https://media.giphy.com/media/Ww3o6lZgrjldYKoHYb/giphy.gif']
    ONEUP_GIFS = ['https://media.giphy.com/media/nNXcXGX65D5rXkpiJd/giphy.gif', 'https://media.giphy.com/media/492eHSGThgIDx0quLA/giphy.gif', 'https://media.giphy.com/media/vYHQeUQKiEKtjFmVVu/giphy.gif', 'https://media.giphy.com/media/r27ezJNGnlIN7eonmn/giphy.gif', 'https://media.giphy.com/media/p0DOA7vgjZIrofqP1K/giphy.gif', 'https://media.giphy.com/media/k9INvJjWU636EnqZv5/giphy.gif', 'https://media.giphy.com/media/bixPdyQVlFCOxWY5Gu/giphy.gif', 'https://media.giphy.com/media/9HhNfrAsBWoG0HpOSa/giphy.gif', 'https://media.giphy.com/media/7nRpNHtUBaw8Go5AwD/giphy.gif',
                  'https://media.giphy.com/media/zJcxfUcjEnHFeEJA3T/giphy.gif', 'https://media.giphy.com/media/PnFQRzb9JQUug3eqvE/giphy.gif', 'https://media.giphy.com/media/ikbRAXLsu6JfnRgSXX/giphy.gif', 'https://media.giphy.com/media/hwTPcbxWMtyc25CGyV/giphy.gif', 'https://media.giphy.com/media/KbdQyDNsPfSjG7kSVM/giphy.gif', 'https://media.giphy.com/media/dkluEGUKdIU1FX8Mlh/giphy.gif', 'https://media.giphy.com/media/0BZZjFyuoDIAR2sHvL/giphy.gif', 'https://media.giphy.com/media/4d2RQZH2tNni28rww9/giphy.gif', 'https://media.giphy.com/media/QXwknhHN7o04AeXcy9/giphy.gif', 'https://media.giphy.com/media/6UwssqVDmfSTAEYhjT/giphy.gif']

    gif_set = PIZZA_GIFS

    # if not category:
    #     guild = str(ctx.guild.name)
    #     if guild == 'Hive Pizza':
    #         gif_set = PIZZA_GIFS
    #     elif guild == 'Rising Star Game':
    #         gif_set = RISINGSTAR_GIFS
    #     else:
    #         gif_set = PIZZA_GIFS
    # elif category.lower() == 'pizza':
    #     gif_set = PIZZA_GIFS
    # elif category.lower() == 'bro':
    #     gif_set = BRO_GIFS
    # elif category.lower() == 'risingstar':
    #     gif_set = RISINGSTAR_GIFS
    # elif category.lower() == 'pob':
    #     gif_set = POB_GIFS
    # elif category.lower() == 'profound':
    #     gif_set = PROFOUND_GIFS
    # elif category.lower() == 'battleaxe':
    #     gif_set = BATTLEAXE_GIFS
    # elif category.lower() == 'england':
    #     gif_set = ENGLAND_GIFS
    # elif category.lower() == 'huzzah':
    #     gif_set = HUZZAH_GIFS
    # elif category.lower() == 'beard':
    #     gif_set = BEARD_GIFS
    # elif category.lower() == 'lego':
    #     gif_set = LEGO_GIFS
    # elif category.lower() == 'blurt':
    #     gif_set = BLURT_GIFS
    # elif category.lower() == 'foxon':
    #     gif_set = FOXON_GIFS
    # elif category.lower() == 'stickup':
    #     gif_set = STICKUP_GIFS
    # elif category.lower() == 'pineapple':
    #     gif_set = PINEAPPLE_GIFS
    # elif category.lower() == 'dibblers':
    #     gif_set = DIBBLERS_GIFS
    # elif category.lower() == 'cine':
    #     gif_set = CINE_GIFS
    # elif category.lower() == '1up':
    #     gif_set = ONEUP_GIFS
    # else:
    #     gif_set = PIZZA_GIFS

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
    wallets_1plus = len([x for x in wallets if float(
        x['balance']) + float(x['stake']) >= 1])

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

    embed = discord.Embed(title='$%s Token Distribution' %
                          symbol, description=message, color=0x43aa8b)
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

    embed = discord.Embed(title='Top 10 $%s Holders' %
                          symbol, description='', color=0xf8961e)

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

    embed = discord.Embed(title='Latest 10 $%s Hive-Engine Transactions' %
                          symbol, description=message, color=0x277da1)
    await ctx.response.send_message(embed=embed)


@bot.tree.command(name="witness", description="Print Hive Witness Info.")
@app_commands.describe(
    witnessname="Name of Hive witness."
)
async def witness(ctx: discord.Interaction, witnessname: str = 'pizza.witness'):
    """<witness name>: Print Hive Witness Info."""
    witnessname = witnessname.lower()
    message_body = '```\n'

    witness = Witness(witnessname, blockchain_instance=hive)

    witness_json = witness.json()
    witness_schedule = hive.get_witness_schedule()
    config = hive.get_config()
    if "VIRTUAL_SCHEDULE_LAP_LENGTH2" in config:
        lap_length = int(config["VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    elif "HIVE_VIRTUAL_SCHEDULE_LAP_LENGTH2" in config:
        lap_length = int(config["HIVE_VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    else:
        lap_length = int(config["STEEM_VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    rank = 0
    active_rank = 0
    found = False
    witnesses = WitnessesRankedByVote(limit=101, blockchain_instance=hive)
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

    embed = discord.Embed(title='Hive Witness info for @%s' %
                          witnessname, description='', color=0xf3722c)
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
    results = hiveengine_api.find(
        'witnesses', 'witnesses', query={})

    results = sorted(results, key=lambda a: float(
        a['approvalWeight']['$numberDecimal']), reverse=True)

    embed = discord.Embed(title='Hive-Engine Witness info for @%s' %
                          witnessname, description='', color=0xf3722c)

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
    results = hiveengine_api.find('marketpools', 'liquidityPositions', query={
                                  "account": "%s" % wallet})
    embed = discord.Embed(title='DIESEL Pool info for @%s' %
                          wallet, description='', color=0xf3722c)

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

    results = hiveengine_api.find('marketpools', 'pools', query={
                                  "tokenPair": {"$in": ["%s" % pool]}})

    embed = discord.Embed(title='DIESEL Pool info for %s' %
                          pool, description='', color=0xf3722c)

    if len(results) == 0:
        embed.add_field(name='DIESEL Pool %s' % pool, value='Not Found')
    else:
        result = results[0]
        for key in result.keys():
            if key not in ['_id', 'precision', 'creator']:
                embed.add_field(name=key, value=result[key], inline=True)

        results = hiveengine_api.find('marketpools', 'liquidityPositions', query={
                                      "tokenPair": {"$in": ["%s" % pool]}})
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

    results = hiveengine_api.find('distribution', 'batches', query=query)

    embed = discord.Embed(title='DIESEL Pool Rewards for %s' %
                          pool, description='', color=0xf3722c)

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
        buy_book = market.get_buy_book(symbol=symbol, limit=1000)
    except hiveengine.exceptions.TokenDoesNotExists:
        await ctx.response.send_message('Error: the Hive-Engine token symbol does not exist.')
        return

    buy_book = sorted(buy_book, key=lambda a: float(a['price']), reverse=True)
    buy_book = buy_book[0:10]

    embed = discord.Embed(title='Buy Book for $%s (first 10 orders)' %
                          symbol.upper(), description='', color=0xf3722c)

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
        sell_book = market.get_sell_book(symbol=symbol, limit=1000)
    except hiveengine.exceptions.TokenDoesNotExists:
        await ctx.response.send_message('Error: the Hive-Engine token symbol does not exist.')
        return

    sell_book = sorted(sell_book, key=lambda a: float(
        a['price']), reverse=False)
    sell_book = sell_book[0:10]

    embed = discord.Embed(title='Sell Book for $%s (first 10 orders)' %
                          symbol.upper(), description='', color=0xf3722c)

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
    api = 'https://api2.splinterlands.com/players/details?name=%s' % player

    profile = requests.get(api).json()

    embed = discord.Embed(title='Splinterlands profile for %s:' %
                          player, description='', color=0x336EFF)

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
    api = 'https://digitalself.io/api_feed/exode/my_delivery_api.php?account=%s&filter=singleCards' % player
    cards = requests.get(api).json()['elements']
    market_prices = [card['market_price'] for card in cards]

    elite_cards = [card for card in cards if card['is_elite']]

    packsapi = 'https://digitalself.io/api_feed/exode/my_delivery_api.php?account=%s&filter=packs' % player
    packs = requests.get(packsapi).json()['elements']
    pack_market_prices = [pack['market_price'] for pack in packs]

    embed = discord.Embed(title='Exode cards for %s:' %
                          player, description='', color=0x336EFF)
    embed.add_field(name='Card count', value=len(cards), inline=True)
    embed.add_field(name='Elite card count',
                    value=len(elite_cards), inline=True)
    embed.add_field(name='Packs count', value=len(packs), inline=True)
    embed.add_field(name='Total market value', value='$%0.3f' %
                    (sum(market_prices)+sum(pack_market_prices)), inline=True)

    await ctx.response.send_message(embed=embed)


# Rising Star related commands
@bot.tree.command(name="rsplayer", description="Check Rising Star Player Stats.")
@app_commands.describe(
    player="Name of player, i.e. thebeardflex."
)
async def rsplayer(ctx: discord.Interaction, player: str):
    """<player>: Check Rising Star Player Stats."""
    api = 'https://www.risingstargame.com/playerstats.asp?player=%s' % player

    try:
        profile = requests.get(api).json()[0]
    except json.decoder.JSONDecodeError:
        await ctx.response.send_message('Error: unable to fetch risingstar data.')
        return

    embed = discord.Embed(title='Rising Star Profile for @%s' %
                          player, description='', color=0xf3722c)

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
    embed = discord.Embed(title='Hive.Pizza links',
                          description='Please consider supporting Hive.Pizza by using these referral links.', color=0xf3722c)
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
    rc = beem.rc.RC(hive_instance=hive)
    comment_cost = rc.comment()
    vote_cost = rc.vote()
    json_cost = rc.custom_json()
    account_cost = rc.claim_account()

    acc = beem.account.Account(wallet, blockchain_instance=hive)
    mana = acc.get_rc_manabar()['current_mana']

    possible_jsons = int(mana / json_cost)
    possible_votes = int(mana / vote_cost)
    possible_comments = int(mana / comment_cost)
    possible_accounts = int(mana / account_cost)

    current_pct = float(acc.get_rc_manabar()['current_pct'])
    embed = discord.Embed(title='Hive Resource Credits for @%s' % wallet,
                          description='RC manabar is at %0.3f%%' % current_pct, color=0xf3722c)
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

    embed = discord.Embed(title='Hive Pizza Systems Status',
                          description='PizzaNet Systems are Operational. :green_circle:', color=0xE31337)

    embed.add_field(name=bot.user, value='Serving %d Discord guilds.\n' % (
        len(bot.guilds)), inline=False)

    for account in accounts:
        acc = beem.account.Account(account, blockchain_instance=hive)
        current_pct = float(acc.get_rc_manabar()['current_pct'])

        extra_info = ''

        if account == 'pizza.witness':
            active_rank = 0
            witnesses = WitnessesRankedByVote(
                limit=101, blockchain_instance=hive)
            for w in witnesses:
                if w.is_active:
                    active_rank += 1
                if w["owner"] == account:
                    break

            extra_info = ' | Active Rank %d' % active_rank

        if account == 'pizza-engine':
            # get HE witness rank
            results = hiveengine_api.find('witnesses', 'witnesses', query={})
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
    HIVESEARCHER_API_KEY = os.getenv('HIVESEARCHER_API_KEY')

    payload = '{"q": "%s", "sort": "%s"}' % (query, sort)
    headers = {'Authorization': HIVESEARCHER_API_KEY,
               'Content-Type': 'application/json'}

    json = requests.post(HIVESEARCHER_URL, data=payload,
                         headers=headers).json()
    results = json['results']

    embed = discord.Embed(title='Hive Content Search Results from HiveSearcher',
                          description='Showing 10 results for %s, sorted by %s\n' % (query, sort), color=0xE31337)
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

@bot.event
async def on_command_error(ctx: discord.Interaction, error: Exception):
    """Print out exception for debugging."""
    if isinstance(error, commands.CommandNotFound):
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


@bot.event
async def on_ready():
    """Event handler for bot comnnection."""
    print(f'{bot.user} has connected to Discord!')
    print('Serving %d Discord guilds.' % len(bot.guilds))
    await update_bot_user_status(bot)

    PizzaCog(bot)

    # bot.tree.clear_commands(guild=None, type=None)
    # await bot.tree.sync()
    # await bot.tree.sync(guild=None)

    await bot.tree.sync(guild=None)


# Discord initialization
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
