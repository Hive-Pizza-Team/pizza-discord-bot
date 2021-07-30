#!/usr/bin/env python3
''' Discord bot for $PIZZA token community '''
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from hiveengine.market import Market
from hiveengine.tokenobject import Token
import random
from pycoingecko import CoinGeckoAPI
import hiveengine
from hiveengine.wallet import Wallet
import json
from hiveengine.api import Api
import beem
from beem.witness import Witness, WitnessesRankedByVote, WitnessesVotedByAccount


# HiveEngine defines
market = Market()
TOKEN_NAME = 'PIZZA'
ACCOUNT_FILTER_LIST = ['thebeardflex','pizzaexpress','hive.pizza','datbeardguy','pizzabot','null','vftlab']

CONFIG_FILE = 'config.json'

# Miscellaneous defines
GITHUB_URL = 'https://github.com/Hive-Pizza-Team/pizza-discord-bot'


PIZZA_GIFS = ['https://files.peakd.com/file/peakd-hive/pizzabot/24243uENGsh6uW4qKCGujxK4BvoMKN5RcN7sfaEJ5NKJtep8rt9afWsVtg3Kvjtq1pDjS.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23zGqBEBBrndd2a4j4sFd7pfokJbPP78MUeXbhTF7tpkm68TDPNKpyEQx6SyXfw2TvxCc.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xouo4FKcHyERYKyiEm4x425LXY5UZsLSbwPtftnNGdqpGPpP9TwJ6k3WfLGw7dRi8ix.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23wqthb5pRQCesbcTuqXfTcNtjLsRRRTpEUfTaMAqm1h8jVmEgYikZjf2edLHrRcoDriQ.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23yd8DEejLwG8jbK6yiHPUqaQqC2rWNvVjANJcC5J5LQM3NKz9SHZZqCy9Lzg1YsnoR5W.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/242DXLG4DJojrUAscw229UnyJkGma6C1QoCQjngcVG2LFbkaTdN4oJw9WgLLxV3N2oWLc.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23sdt4qbqaFxwbYhkYuviGR8kBeGLTYeaveqjXiwGSRUbxyV5J5rusMoXD1AGk2JhpDsi.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23wX5M8YHK92Kzmr8gAE1mZRePnsG96StjiPPnDYGcdq6BD3BkmMb7jLrCiPVrGRKsbBi.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xL35bVpiQbPTwnuBMMPsEpSbApf598uVE9fMXq8SKj5Hzh2ik4CnHYWcRNBriXkk5gQ.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/242DQXTLyKebw5oUNSqsNPvoqPDXCgPKafnoB2zE7bBqyfCAKxKL44r4SarskWCmYY4Lc.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/242s64cMzwVBDgMuApdLgtJrj4G4Qt3dTjJuKWFb4MXCvwiXAorV25iTUMFjU4gPm1azQ.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23y92ccQqXL7ixb1AYUg8T6yHRAEiLptBYhuoahFeh8uU8FXt1WFhJBwLysktbFdC46Gc.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/242Nt1WKYcjivqc1FPyfqwQ6vkTs7sznxWKYagPhc7TQ4v8VSYNA46NEswjkZeiSxuRAC.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xKxeFC2EKESp2cQ3MrPHcAHEaFtvf2mekStgrqqSxYS5rL7PnfmNwoWVQbdJwJS6zQt.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/242hfEv5oigYcb19z6ZDEPANTmAn1rWub84KKSJqdbtenEWhPxK2H1tqwanWzTrXZC3LQ.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xerFt4yJKoK1hhVdzVEYpKMKbGUHaW9SR3g7os8UmqAZLsnhs5QgWGeD9NNk72FNGxC.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/243Bpw3x8jfheRpNACEc9fjrrLvn2Qtw8KQwhwscRjLc8BNfhxktPjuLDvnjTv7wCeLVi.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xAcRA5z5PG8aNLzq3jcDrSwP6eVYAagSSooGTzWQ4TZHPvNH8Ccc16zwtP6y3fkgX1e.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23zGkxUGqyXMTN7rVm2EPkLr6dsnk4T4nFyrEBejS9WB2VbKpJ3P356EcQjcrMF6gRTbz.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23x17QUuztsLf64Mav8m59nuRF4B9k3RAV6QGrtpvmc3hA9bxSJ2URkW7fuYSfaRLKAq2.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23wC5ZpMMfnFCsLS4MLF3N6XZ2aMQ1Fjnw6QGrZtpJqQmiH4xtsUEgjjCD5VU3ccjoRet.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xpKDUUZXfKhB9t5HqVEyqqd9ryYUkwTE2fgfZR6wAyzkPrjUY9rMpSP6zkrmXTUtBCQ.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23wr1XodaTgJAVzDu9sEV7q5r6RV3QppV2Nvxty4vD6BwYdHQLKGhgsynnz4fFC2GYyZW.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23wr1BUi29btm7eRvcRbqee2e52DCmH5x5HWLVrrQ7GqLc5UQMYawfsHTAsgCLghj5Kwa.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23z7SiUwzPi3WQ1nS8Lk4qBUqKtmgZRRTuQZP54mRiDpi8A22pk1ScoFgVa8CyhqQsAuS.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xpJztdYA9RpUnMRWDyYsWyixmqFMRSpix52vvx1vuxJSZHJL45YWmb9rUsswymZaSFE.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xyhemVn25gUt2p6JCHQ3hBjJyaz7d8hvmNusti9GNbjj8jToVFL4FaouPhkVoRYNnng.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/Ep1ZrmXNXjF4ZEYpXjJAVNThmFrQT3m4Q6jfxreCg1w7z81af8DHHZzeKk9QKy1Got8.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23wqwJUY56PuyQS3doAHbLfsjnNTcqLUry1cSmoSyGmRc49BswoxTGYhySmrXuevYWCJg.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23yTqi8V4mqNvq5nfFNt69AC2tMc5ou3FZ6r9AzfxuPEyQbrX8CBDEMXcjNNmTMTCMnXv.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/242DhzmX9cZCijjJpD1qwqvcRdJMHPsxvsfesBYkQUVpXpn5s3g9SewPCeiJ1ne4zUC7N.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xpKbgbo6LSPutm7ntaeVDiVJfdaxiJGhs8N4sve1MNdENuRAKw37uJbutCNBqj2M7vU.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/EopwGAarumCksxjQEeMsTXTDeMw16kD35cciBsiJFWbbBV8nGVyGAXtn4tScHTWQmvC.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23wgeYo6ULhiwyKEtKNpNfyU3oEn9zWJpKbSU2Hj5u11rn2YQr2wNoUUVrv1bBvMHgifn.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23xyfe5dT4xLHwJbamNCJUXpQuuV9kLucPMPXJsi74VoLq5bHBTrdkhVjyagno78r3F1n.gif',
'https://files.peakd.com/file/peakd-hive/pizzabot/23wMihvfhNfs4b1MKhb9bNdhEbeZoXTDkud331QCbL64zaxG6p9GuAbydjEUVczCDd49i.gif'
]


def read_config_file():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as configfile:
            configs = json.load(configfile)
            custom_prefixes = configs['custom_prefixes']

            return custom_prefixes
    else:
        return {}


def write_config_file(custom_prefixes):
    with open(CONFIG_FILE, 'w') as configfile:
        configfile.write(json.dumps({'custom_prefixes': custom_prefixes}))


async def determine_prefix(bot, message):

    guild = message.guild
    #Only allow custom prefixes in guild
    if guild:
        return custom_prefixes.get(str(guild.id), default_prefix)
    else:
        return default_prefix


def get_token_holders(symbol):

    holder_count = 1000
    token_holders = []
    while holder_count == 1000:
        response = Token(symbol).get_holder(offset=len(token_holders))
        holder_count = len(response)
        token_holders += response

    return token_holders


def get_token_price_he_cg(coin):
    coin = coin.lower()

    if coin == 'eth':
        coin = 'ethereum'
    elif coin == 'btc':
        coin = 'bitcoin'
    
    found_in_hiveengine = False
    try:
        Token(coin)
        found_in_hiveengine = True
        hive_usd = get_coin_price()

        last_price = 0.0
        lowest_asking_price = 0.0
        highest_bidding_price = 0.0

        trade_history = market.get_trades_history(symbol=coin, limit=1000)
        if trade_history: last_price = float(trade_history[-1]['price'])
        last_usd = last_price * hive_usd

        sell_book = market.get_sell_book(symbol=coin, limit=1000)
        sell_book = sorted(sell_book, key= lambda a: float(a['price']), reverse=False)
        if sell_book: lowest_asking_price = float(sell_book[0]['price'])
        ask_usd  = lowest_asking_price * hive_usd

        buy_book = market.get_buy_book(symbol=coin, limit=1000)
        buy_book = sorted(buy_book, key= lambda a: float(a['price']), reverse=True)
        if buy_book: highest_bidding_price = float(buy_book[0]['price'])
        bid_usd  = highest_bidding_price * hive_usd

        embed = discord.Embed(title='HiveEngine market info for $%s' % coin.upper(), last_usd='', color=0xf3722c)
        embed.add_field(name='Last', value='%.5f HIVE | $%.5f USD' % (last_price, bid_usd), inline=False)
        embed.add_field(name='Ask', value='%.5f HIVE | $%.5f USD' % (lowest_asking_price, ask_usd), inline=False)
        embed.add_field(name='Bid', value='%.5f HIVE | $%.5f USD' % (highest_bidding_price, bid_usd), inline=False)
        return embed

    except hiveengine.exceptions.TokenDoesNotExists:
        print('Token not found in HE, trying CoinGeckoAPI')

    if not found_in_hiveengine:
        price = get_coin_price(coin)
        message = '''```fix
market price: $%.5f USD
```''' % (price)

        embed = discord.Embed(title='CoinGecko market info for $%s' % coin.upper(), description=message, color=0xf3722c)
        return embed


def get_coin_price(coin='hive'):
    ''' Call into coingeck to get USD price of coins i.e. $HIVE '''
    coingecko = CoinGeckoAPI()
    response = coingecko.get_price(ids=coin, vs_currencies='usd')

    if coin not in response.keys():
        print('Error calling CoinGeckoAPI for %s price' % coin)
        return -1

    subresponse = response[coin]
    if 'usd' not in subresponse.keys():
        print('Error 2 calling CoinGeckoAPI for %s price' % coin)
        return -1

    return float(subresponse['usd'])


def get_hiveengine_history(token='PIZZA'):

    message = '''```fix
'''

    for tx in market.get_trades_history(symbol=token, limit=1000)[::-1][0:10]:
        message += '%0.4f @ %0.4f HIVE: %s -> %s\n' % (float(tx['quantity']), float(tx['price']), tx['seller'], tx['buyer'])

    message += '```'

    return message


async def update_bot_user_status():

    last_price = float(market.get_trades_history(symbol=TOKEN_NAME)[-1]['price'])
    last_price_usd = round(get_coin_price() * last_price, 3)
    await bot.change_presence(activity=discord.Game('PIZZA ~ $%.3f USD' % last_price_usd))


custom_prefixes = read_config_file()
default_prefix = '!'
bot = commands.Bot(command_prefix = determine_prefix)


@bot.event
async def on_ready():
    await update_bot_user_status()
    print(f'{bot.user} has connected to Discord!')


@bot.command()
@commands.guild_only()
async def prefix(ctx, arg=''):
    """<prefix> : Print and change bot's command prefix"""
    # get current prefix
    if arg == '':
        prefix = await determine_prefix(bot, ctx.message)
        guild = ctx.message.guild

        await ctx.send('Current prefix is: %s for guild: %s' % (prefix,guild))

    else:
        guild = ctx.message.guild
        if not ctx.message.author.guild_permissions.administrator:
            await ctx.send('You must be an admin to change my command prefix for guild: %s' % (guild))
            return

        custom_prefixes[str(guild.id)] = arg
        await ctx.send('Changed prefix to: %s for guild: %s' % (arg,guild))
        write_config_file(custom_prefixes)


def get_hive_power_delegations(wallet):

    hive = beem.hive.Hive()
    acc = beem.account.Account(wallet)

    incoming_delegations_total = 0

    delegations = acc.get_vesting_delegations()

    for delegation in delegations:
        hive_power = hive.vests_to_token_power(delegation['vesting_shares']['amount']) / 10 ** delegation['vesting_shares']['precision']
        incoming_delegations_total += hive_power

    return incoming_delegations_total


@bot.command()
async def bal(ctx, wallet, symbol=''):
    """<wallet> <symbol> : Print HiveEngine wallet balances"""

    if symbol == '':
        symbol = TOKEN_NAME

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
        wallet_token_info = Wallet(wallet).get_token(symbol)

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

    embed = discord.Embed(title='Balances for @%s' % wallet, description='$%s' % symbol, color=0x336EFF)
    embed.add_field(name='Liquid', value='%0.3f' % (balance), inline=False)
    embed.add_field(name='Staked', value='%0.3f' % (staked), inline=False)

    if delegation_in > 0:
        embed.add_field(name='Incoming Delegation', value='%0.3f' % (delegation_in), inline=False)
    if delegation_out > 0:
        embed.add_field(name='Outgoing Delegation', value='%0.3f' % (delegation_out), inline=False)

    total = balance + staked + delegation_in - delegation_out
    embed.add_field(name='Total', value='%0.3f' % (total), inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def bals(ctx, wallet):
    """<wallet>: Print HiveEngine wallet balances"""

    # hive engine token
    wallet = wallet.lower()
    wallet_token_info = Wallet(wallet)

    # sort by stake then balance
    wallet_token_info.sort(key=lambda elem: float(elem['stake']) + float(elem['balance']))
    wallet_token_info = wallet_token_info[::-1]

    longest_symbol_len = 0
    for token in wallet_token_info:
        if len(token['symbol']) > longest_symbol_len:
            longest_symbol_len = len(token['symbol'])


    message_body = '```'
    message_body += 'SYMBOL'.ljust(longest_symbol_len, ' ') + ' |  LIQUID  |  STAKED  | INCOMING | OUTGOING\n'

    rows = []

    for token in wallet_token_info:
        symbol = token['symbol']
        balance = float(token['balance'])
        staked = float(token['stake'])
        delegation_in = float(token['delegationsIn'])
        delegation_out = float(token['delegationsOut'])

        padded_symbol = symbol.ljust(longest_symbol_len, ' ')
        rows.append('%s |%10.3f|%10.3f|%10.3f|%9.3f\n' % (padded_symbol, balance, staked, delegation_in, delegation_out))

    for row in rows[0:10]:
        message_body += row

    message_body += '```'

    embed = discord.Embed(title='First 10 balances for @%s' % wallet, description=message_body, color=0x90be6d)
    await ctx.send(embed=embed)


@bot.command()
async def price(ctx, symbol=''):
    """<symbol> : Print HiveEngine market price info"""
    await update_bot_user_status()

    if symbol == '':
        symbol = TOKEN_NAME

    embed = get_token_price_he_cg(symbol)
    await ctx.send(embed=embed)


@bot.command()
async def gif(ctx):
    """ Drop a random GIF! """
    response = random.choice(PIZZA_GIFS)
    await ctx.send(response)


@bot.command()
async def info(ctx):
    """ Print Hive.Pizza project link """
    response = '''Learn more about $PIZZA @ https://hive.pizza'''
    await ctx.send(response)


@bot.command()
async def tokenomics(ctx, symbol=''):
    """<symbol> : Print HiveEngine token distribution info"""

    if symbol == '':
        symbol = TOKEN_NAME

    wallets = [x for x in get_token_holders(symbol) if x['account'] not in ACCOUNT_FILTER_LIST]

    total_wallets = len([x for x in wallets if float(x['balance']) + float(x['stake']) > 0])

    # count wallets with at least 1 token
    wallets_1plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 1])

    # count wallets with at least 20 tokens
    wallets_20plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 20])

    # count wallets with at least 200 tokens
    wallets_200plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 200])

    # count wallets with at least 1000 tokens
    wallets_1000plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 1000])

    # count wallets with at least 1000 tokens
    wallets_10000plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 10000])

    message = '''```
%.4d wallets hold >       0 $%s
%.4d wallets hold >=      1 $%s ( 8-) )
%.4d wallets hold >=     20 $%s (bot access level 1)
%.4d wallets hold >=    200 $%s (bot access level 2)
%.4d wallets hold >=  1,000 $%s (badass level)
%.4d wallets hold >= 10,000 $%s (baron level)
```''' % (total_wallets, symbol, wallets_1plus, symbol, wallets_20plus, symbol, wallets_200plus, symbol, wallets_1000plus, symbol, wallets_10000plus, symbol)

    embed = discord.Embed(title='$%s Token Distribution' % symbol, description=message, color=0x43aa8b)
    await ctx.send(embed=embed)


@bot.command()
async def source(ctx):
    """ Print my source code location """
    response = 'My source code is found here: %s' % GITHUB_URL
    await ctx.send(response)


@bot.command()
async def top10(ctx, symbol=''):
    """<symbol> : Print HiveEngine token rich list top 10"""
    if symbol == '':
        symbol = TOKEN_NAME


    accounts = [x for x in get_token_holders(symbol) if x['account'] not in ACCOUNT_FILTER_LIST]
    accounts = sorted(accounts, key= lambda a: float(a['stake']), reverse=True)

    # identify the top 10 token holders
    top10 = [(x['account'], float(x['stake'])) for x in accounts[0:10]]

    count = 0

    embed = discord.Embed(title='Top 10 $%s Stakers' % symbol, description='', color=0xf8961e)
    for account, balance in top10:
        count += 1
        embed.add_field(name='%d. %s' % (count,account), value=balance, inline=True)

    await ctx.send(embed=embed)


@bot.command()
async def history(ctx, symbol=''):
    """<symbol> : Print recent HiveEngine token trade history"""
    if symbol == '':
        symbol = TOKEN_NAME

    response = get_hiveengine_history(symbol)

    embed = discord.Embed(title='Latest 10 $%s HiveEngine Transactions' % symbol, description=response, color=0x277da1)
    await ctx.send(embed=embed)


@bot.command()
async def blog(ctx, name=''):
    """<symbol> : Link to last post from blog"""

    if name == '':
        name = 'thebeardflex'

    from beem.discussions import Query, Discussions_by_blog
    q = Query(limit=10, tag=name)
    latest_blog = Discussions_by_blog(q)[0]

    reply_identifier = '@%s/%s' % (latest_blog['author'], latest_blog['permlink'])

    response = 'Latest post from @%s: https://peakd.com/%s' % (name, reply_identifier)

    await ctx.send(response)

@bot.command()
async def farms(ctx):
    """Print $PIZZA VFT Farm deposits"""

    api = Api()

    deposits = {}
    total_deposits = 0
    longest_name_len = 0

    for tx in api.get_history("vftlab", "PIZZA"):

        quantity = float(tx['quantity'])
        to = tx['to']
        tfrom = tx['from']

        if len(tfrom) > longest_name_len:
            longest_name_len = len(tfrom)

        if tfrom == 'vftlab':
            total_deposits -= quantity

            if to in deposits.keys():
                deposits[to] -= quantity
            else:
                deposits[to] = -1 * quantity
        else:
            total_deposits += quantity

            if tfrom in deposits.keys():
                deposits[tfrom] += quantity - quantity * 0.03
            else:
                deposits[tfrom] = quantity - quantity * 0.03

    list_deposits = []
    for depositor in deposits.keys():
        list_deposits.append({'name':depositor,'balance':deposits[depositor],'payout': 50 * deposits[depositor] / total_deposits})


    list_deposits.sort(key= lambda a: float(a['balance']), reverse=True)


    response = '''```fix
'''

    response += 'Depositor'.ljust(longest_name_len, ' ') + ' | $PIZZA Amount | Expected Daily Payout ($VFT)\n'

    for deposit in list_deposits[0:30]:
        response += '%s | %13.3f | %8.3f\n' % (deposit['name'].ljust(longest_name_len, ' '), deposit['balance'], deposit['payout'])

    response += '```'

    embed = discord.Embed(title='Top 30 Pizza Farm deposits:', description=response, color=0x277da1)
    await ctx.send(embed=embed)


@bot.command()
async def witness(ctx, name='pizza.witness'):
    """Print Hive Witness Info"""
    name = name.lower()
    message_body = '```\n'

    hive = beem.Hive()
    witness = Witness(name, blockchain_instance=hive)

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
    virtual_time_to_block_num = int(witness_schedule["num_scheduled_witnesses"]) / (lap_length / (vote_sum + 1))

    virtual_diff = int(witness_json["virtual_scheduled_time"]) - int(witness_schedule['current_virtual_time'])
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

    embed = discord.Embed(title='Witness info for @%s' % name, description='', color=0xf3722c)
    embed.add_field(name='Running Version', value=witness_json['running_version'], inline=False)
    embed.add_field(name='Missing Blocks', value=witness_json['total_missed'], inline=False)

    if est_time_to_next_block:
        embed.add_field(name='Estimate time to next block', value=est_time_to_next_block, inline=False)

    if found:
        embed.add_field(name='Rank', value='%d' % rank, inline=False)
        embed.add_field(name='Active Rank', value='%d' % active_rank, inline=False)


    await ctx.send(embed=embed)


# Discord initialization
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')



bot.run(TOKEN)
