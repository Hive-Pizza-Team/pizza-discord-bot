"""Utility helpers for the pizza discord bot."""
import logging
from typing import Dict, Optional, Tuple

from discord import Embed, Interaction
from pycoingecko import CoinGeckoAPI
import hiveengine
from hiveengine.tokenobject import Token
from utils_hiveengine import (
    get_hiveengine_instance,
    get_hiveengine_market_instance,
    get_market_history,
)
from utils_hive import get_hive_instance
import requests

logger = logging.getLogger(__name__)

BRAND_COLOR = 0xf3722c
FOOTER_TEXT = 'by hive.pizza team'
FOOTER_ICON = 'https://hive.pizza/wp-content/uploads/2022/01/cropped-officialpizzalogo1-32x32.png'


def make_embed(title: str = '', description: str = '',
               color: Optional[int] = None) -> Embed:
    """Create an Embed with consistent branding."""
    embed = Embed(
        title=title,
        description=description,
        color=color or BRAND_COLOR,
    )
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
    return embed


def determine_native_token(ctx: Interaction,
                           default_token_name: str) -> str:
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


def get_token_price_he_cg(coin: str) -> Embed:
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

        Token(coin, api=get_hiveengine_instance())
        found_in_hiveengine = True
        hive_usd = get_coin_price()[0]

        last_price = 0.0
        lowest_asking_price = 0.0
        highest_bidding_price = 0.0

        trade_history = get_market_history(symbol=coin)
        if trade_history:
            last_price = float(trade_history[-1]['price'])
        last_usd = last_price * hive_usd

        sell_book = get_hiveengine_market_instance().get_sell_book(
            symbol=coin, limit=1000)
        sell_book = sorted(sell_book, key=lambda a: float(
            a['price']), reverse=False)
        if sell_book:
            lowest_asking_price = float(sell_book[0]['price'])
        ask_usd = lowest_asking_price * hive_usd

        buy_book = get_hiveengine_market_instance().get_buy_book(
            symbol=coin, limit=1000)
        buy_book = sorted(buy_book, key=lambda a: float(
            a['price']), reverse=True)
        if buy_book:
            highest_bidding_price = float(buy_book[0]['price'])
        bid_usd = highest_bidding_price * hive_usd

        url = 'https://history.hive-engine.com/marketHistory'
        volume_data = requests.get(
            url,
            params={'symbol': coin.upper()},
            timeout=10,
        ).json()
        volume_str = '%s %s | %s HIVE\n' % (
            volume_data[0]['volumeToken'],
            volume_data[0]['symbol'],
            volume_data[0]['volumeHive'],
        )

        embed = make_embed(
            title='Hive-Engine market info for $%s' % coin.upper())
        embed.add_field(name='Last', value='%.5f HIVE | $%.5f' %
                        (last_price, last_usd), inline=False)
        embed.add_field(name='Ask', value='%.5f HIVE | $%.5f' %
                        (lowest_asking_price, ask_usd), inline=False)
        embed.add_field(name='Bid', value='%.5f HIVE | $%.5f' %
                        (highest_bidding_price, bid_usd), inline=False)
        embed.add_field(
            name='Today Volume', value=volume_str, inline=False)
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

        embed = make_embed(
            title='CoinGecko market info for $%s' % coin.upper(),
            description=message)

        if coin == 'hive_dollar':
            internal = get_hive_internal_hbd_price()
            if internal:
                hbd_per_hive = 1.0 / internal['hbd_hive_price']
                hbd_usd = hbd_per_hive * internal['feed_price']
                embed.add_field(
                    name='Hive Internal Market',
                    value='```fix\nHBD price: $%.5f\n```' % hbd_usd,
                    inline=False)

        return embed


def get_hive_internal_hbd_price() -> Optional[Dict[str, float]]:
    """Get HBD price info from the Hive internal market."""
    try:
        from beem.market import Market
        hive = get_hive_instance()
        m = Market(blockchain_instance=hive)
        ticker = m.ticker()
        hbd_hive_price = float(ticker['latest'])
        feed_price = float(hive.get_median_price())
        return {
            'hbd_hive_price': hbd_hive_price,
            'feed_price': feed_price,
        }
    except Exception as e:
        logger.error('Error getting internal HBD price: %s', e)
        return None


def get_coin_price(
    coin: str = 'hive',
) -> Tuple[float, float, float]:
    """Call into CoinGecko to get price of coins i.e. HIVE."""
    coingecko = CoinGeckoAPI()
    try:
        response = coingecko.get_price(
            ids=coin, vs_currencies='usd',
            include_24hr_change='true',
            include_24hr_vol='true')
    except UnboundLocalError:
        logger.error('Error calling CoinGeckoAPI for %s price', coin)
        return (-1, -1, -1)

    if coin not in response.keys():
        logger.error('Error calling CoinGeckoAPI for %s price', coin)
        return (-1, -1, -1)

    subresponse = response[coin]
    if 'usd' not in subresponse.keys():
        logger.error(
            'Error calling CoinGeckoAPI for %s price (missing usd)',
            coin)
        return (-1, -1, -1)

    return (
        float(subresponse['usd']),
        float(subresponse['usd_24h_change']),
        float(subresponse['usd_24h_vol']),
    )
