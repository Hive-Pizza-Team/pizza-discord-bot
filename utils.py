"""Utility helpers for the pizza discord bot."""
from discord import Interaction, Embed
from pycoingecko import CoinGeckoAPI
import hiveengine
from hiveengine.tokenobject import Token
from utils_hiveengine import get_hiveengine_instance, get_hiveengine_market_instance, get_market_history
import requests

hiveengine_api = get_hiveengine_instance()
market = get_hiveengine_market_instance()


def determine_native_token(ctx: Interaction, default_token_name: str) -> str:
    """Determine which token symbol to use by default in the server."""

    if not hasattr(ctx.user, 'guild'):
        return default_token_name

    guild = str(ctx.user.guild.name)

    if guild == 'Hive Pizza':
        return default_token_name
    elif guild == 'Hive':
        return 'HIVE'
    elif guild == 'Rising Star Game':
        return 'STARBITS'
    elif guild == 'The Man Cave':
        return 'BRO'
    elif guild == 'CTP Talk':
        return 'CTP'
    elif guild == 'The Cartel':
        return 'ONEUP'
    else:
        return default_token_name


def get_token_price_he_cg(coin):
    """Get prices of token from Hive-Engine or CoinGecko."""
    coin = coin.lower()

    if coin == 'eth':
        coin = 'ethereum'
    elif coin == 'btc':
        coin = 'bitcoin'
    elif coin == 'cro':
        coin = 'crypto-com-chain'
    elif coin == 'polygon' or coin == 'matic':
        coin = 'matic-network'
    elif coin == 'hbd':
        coin = 'hive_dollar'

    found_in_hiveengine = False
    try:
        if coin == 'hive':
            raise hiveengine.exceptions.TokenDoesNotExists(
                'skip HE query to avoid empty response')

        Token(coin, api=hiveengine_api)
        found_in_hiveengine = True
        hive_usd = get_coin_price()[0]

        last_price = 0.0
        lowest_asking_price = 0.0
        highest_bidding_price = 0.0

        trade_history = get_market_history(symbol=coin)
        if trade_history:
            last_price = float(trade_history[-1]['price'])
        last_usd = last_price * hive_usd

        sell_book = market.get_sell_book(symbol=coin, limit=1000)
        sell_book = sorted(sell_book, key=lambda a: float(
            a['price']), reverse=False)
        if sell_book:
            lowest_asking_price = float(sell_book[0]['price'])
        ask_usd = lowest_asking_price * hive_usd

        buy_book = market.get_buy_book(symbol=coin, limit=1000)
        buy_book = sorted(buy_book, key=lambda a: float(
            a['price']), reverse=True)
        if buy_book:
            highest_bidding_price = float(buy_book[0]['price'])
        bid_usd = highest_bidding_price * hive_usd

        MARKET_HISTORY_URL = 'https://history.hive-engine.com/marketHistory?symbol=%s&volumetoken'
        volume_data = requests.get(MARKET_HISTORY_URL % coin.upper()).json()
        volume_str = '%s %s | %s HIVE\n' % (
            volume_data[0]['volumeToken'], volume_data[0]['symbol'], volume_data[0]['volumeHive'])

        embed = Embed(title='Hive-Engine market info for $%s' %
                      coin.upper(), color=0xf3722c)
        embed.add_field(name='Last', value='%.5f HIVE | $%.5f' %
                        (last_price, last_usd), inline=False)
        embed.add_field(name='Ask', value='%.5f HIVE | $%.5f' %
                        (lowest_asking_price, ask_usd), inline=False)
        embed.add_field(name='Bid', value='%.5f HIVE | $%.5f' %
                        (highest_bidding_price, bid_usd), inline=False)
        embed.add_field(name='Today Volume', value=volume_str, inline=False)
        return embed

    except hiveengine.exceptions.TokenDoesNotExists:
        pass

    if not found_in_hiveengine:
        price, daily_change, daily_volume = get_coin_price(coin)

        if int(price) == -1:
            message = 'Failed to find coin or token called $%s' % coin
        else:
            message = '''```fix
market price: $%.5f
24 hour change: %.3f%%
24 hour volume: $%s
```''' % (price, daily_change, "{:,.2f}".format(daily_volume))

        embed = Embed(title='CoinGecko market info for $%s' %
                      coin.upper(), description=message, color=0xf3722c)
        return embed


def get_coin_price(coin='hive'):
    """Call into coingeck to get price of coins i.e. HIVE."""
    coingecko = CoinGeckoAPI()
    try:
        response = coingecko.get_price(
            ids=coin, vs_currencies='usd', include_24hr_change='true', include_24hr_vol='true')
    except UnboundLocalError:
        print('Error calling CoinGeckoAPI for %s price' % coin)
        return (-1, -1, -1)

    if coin not in response.keys():
        print('Error calling CoinGeckoAPI for %s price' % coin)
        return (-1, -1, -1)

    subresponse = response[coin]
    if 'usd' not in subresponse.keys():
        print('Error 2 calling CoinGeckoAPI for %s price' % coin)
        return (-1, -1, -1)

    return float(subresponse['usd']), float(subresponse['usd_24h_change']), float(subresponse['usd_24h_vol'])
