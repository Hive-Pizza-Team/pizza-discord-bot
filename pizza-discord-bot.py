#!/usr/bin/env python3
''' Discord bot for $PIZZA token community '''
import os
import discord
from dotenv import load_dotenv
from hiveengine.market import Market
from hiveengine.tokenobject import Token
import random
from pycoingecko import CoinGeckoAPI
import hiveengine

# Discord initialization
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()


# HiveEngine defines
market = Market()
TOKEN_NAME = 'PIZZA'
ACCOUNT_FILTER_LIST = ['thebeardflex','pizzaexpress','hive.pizza','datbeardguy','pizzabot']


# Miscellaneous defines
GITHUB_URL = 'https://github.com/hiveuprss/pizza-discord-bot'


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
'https://files.peakd.com/file/peakd-hive/pizzabot/23wC5ZpMMfnFCsLS4MLF3N6XZ2aMQ1Fjnw6QGrZtpJqQmiH4xtsUEgjjCD5VU3ccjoRet.gif']


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

        trade_history = market.get_trades_history(symbol=coin)
        if trade_history: last_price = float(trade_history[-1]['price'])
        last_usd = last_price * hive_usd

        sell_book = market.get_sell_book(symbol=coin)
        if sell_book: lowest_asking_price = float(sell_book[-1]['price'])
        ask_usd  = lowest_asking_price * hive_usd

        buy_book = market.get_buy_book(symbol=coin)
        if buy_book: highest_bidding_price = float(buy_book[-1]['price'])
        bid_usd  = highest_bidding_price * hive_usd


        message = '''```fix
HiveEngine market info for $%s
* last: %.5f HIVE | $%.5f USD
* ask : %.5f HIVE | $%.5f USD
* bid : %.5f HIVE | $%.5f USD
```''' % (coin, last_price, last_usd, lowest_asking_price, ask_usd, highest_bidding_price, bid_usd)
        return message

    except hiveengine.exceptions.TokenDoesNotExists:
        print('Token not found in HE, trying CoinGeckoAPI')

    if not found_in_hiveengine:
        price =  get_coin_price(coin)
        message = '''```fix
CoinGecko market info for $%s
* market price: $%.5f USD
```''' % (coin, price)
        return message


def get_top10_holders():
    accounts = [x for x in Token(TOKEN_NAME).get_holder() if x['account'] not in ACCOUNT_FILTER_LIST]
    accounts = sorted(accounts, key= lambda a: float(a['balance']), reverse=True)

    # identify the top 10 token holders
    top10 = [(x['account'],x['balance']) for x in accounts[0:10]]

    top10str = ''
    for account, balance in top10:
        top10str += '%s - %s\n' % (account, balance)

    message = '''```fix
Top 10 $PIZZA Holders --
%s
```''' % top10str

    return message

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


def get_tokenomics():
    wallets = [x for x in Token(TOKEN_NAME).get_holder()]

    total_wallets = len(wallets)

    # count wallets with at least 1 token
    wallets_1plus = len([x for x in wallets if float(x['balance']) >= 1])

    # count wallets with at least 20 tokens
    wallets_20plus = len([x for x in wallets if float(x['balance']) >= 20])

    # count wallets with at least 20 tokens
    wallets_100plus = len([x for x in wallets if float(x['balance']) >= 100])


    message = '''```css
$PIZZA tokenomics --
%.4d wallets hold $PIZZA
%.4d wallets hold >= 1 $PIZZA   ( 8-) )
%.4d wallets hold >= 20 $PIZZA  (bot access level)
%.4d wallets hold >= 100 $PIZZA (badass level)
```''' % (total_wallets, wallets_1plus, wallets_20plus, wallets_100plus)

    return message


async def update_bot_user_status():

    last_price = float(market.get_trades_history(symbol=TOKEN_NAME)[-1]['price'])
    last_price_usd = round(get_coin_price() * last_price, 3)
    await client.change_presence(activity=discord.Game('PIZZA ~ $%.3f USD' % last_price_usd))


@client.event
async def on_ready():
    await update_bot_user_status()
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!help':
        response = '''```fix
Commands:
!help       : print this message
!price      : print market info
!top10      : print top10 token holders (excluding project accounts)
!tokenomics : print token statistics
!gif        : show me a pizza gif!
!info       : learn more about $PIZZA
!source     : print location of my source code

```'''
        await message.channel.send(response)

    if message.content == '!price':
        await update_bot_user_status()

        last_price = float(market.get_trades_history(symbol=TOKEN_NAME)[-1]['price'])
        lowest_asking_price = float(market.get_sell_book(symbol=TOKEN_NAME)[-1]['price'])
        highest_bidding_price = float(market.get_buy_book(symbol=TOKEN_NAME)[-1]['price'])

        hive_usd = get_coin_price()

        last_usd = last_price * hive_usd
        ask_usd  = lowest_asking_price * hive_usd
        bid_usd  = highest_bidding_price * hive_usd

        response = '''```fix
HiveEngine market info for $%s
* last: %.5f HIVE | $%.5f USD
* ask : %.5f HIVE | $%.5f USD
* bid : %.5f HIVE | $%.5f USD
```''' % (TOKEN_NAME, last_price, last_usd, lowest_asking_price, ask_usd, highest_bidding_price, bid_usd)
        await message.channel.send(response)

    elif message.content.startswith('!price'):
        symbol = message.content.split(' ')[1]
        if symbol:
            response = get_token_price_he_cg(symbol)
            await message.channel.send(response)


    if message.content == '!gif':
        response = random.choice(PIZZA_GIFS)
        await message.channel.send(response)

    if message.content == '!info':
        response = '''```fix
Learn more about $PIZZA @ https://hive.pizza```'''
        await message.channel.send(response)

    if message.content == '!tokenomics':
        response = get_tokenomics()
        await message.channel.send(response)

    if message.content == '!source':
        response = 'My source code is found here: %s' % GITHUB_URL
        await message.channel.send(response)

    if message.content == '!top10':
        response = get_top10_holders()
        await message.channel.send(response)


client.run(TOKEN)
