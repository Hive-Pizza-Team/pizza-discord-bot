#!/usr/bin/env python3
''' Discord bot for $PIZZA token community '''
import os
import discord
from dotenv import load_dotenv
from hiveengine.market import Market
from hiveengine.tokenobject import Token
import random


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


@client.event
async def on_ready():

    last_price = market.get_trades_history(symbol=TOKEN_NAME)[-1]['price']
    await client.change_presence(activity=discord.Game('$PIZZA ~ %.3f Hive' % round(float(last_price), 3)))
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
        last_price = market.get_trades_history(symbol=TOKEN_NAME)[-1]['price']
        await client.change_presence(activity=discord.Game('$PIZZA ~ %.3f Hive' % round(float(last_price), 3)))
        lowest_asking_price = market.get_sell_book(symbol=TOKEN_NAME)[-1]['price']
        highest_bidding_price = market.get_buy_book(symbol=TOKEN_NAME)[-1]['price']
        response = '''```fix
HiveEngine market info for $%s
* last: %s Hive
* ask : %s Hive
* bid : %s Hive
```''' % (TOKEN_NAME, last_price, lowest_asking_price, highest_bidding_price)
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
