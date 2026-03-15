"""Tests for utils.py."""
from unittest.mock import MagicMock, patch

from utils import (
    determine_native_token,
    get_coin_price,
    get_hive_internal_hbd_price,
    get_token_price_he_cg,
)


# ---------------------------------------------------------------------------
# determine_native_token
# ---------------------------------------------------------------------------

class TestDetermineNativeToken:
    def _make_ctx(self, guild_name=None):
        ctx = MagicMock()
        if guild_name is None:
            del ctx.user.guild  # hasattr will return False
        else:
            ctx.user.guild.name = guild_name
        return ctx

    def test_no_guild(self):
        ctx = self._make_ctx(None)
        assert determine_native_token(ctx, 'PIZZA') == 'PIZZA'

    def test_hive_pizza_guild(self):
        ctx = self._make_ctx('Hive Pizza')
        assert determine_native_token(ctx, 'PIZZA') == 'PIZZA'

    def test_hive_guild(self):
        ctx = self._make_ctx('Hive')
        assert determine_native_token(ctx, 'PIZZA') == 'HIVE'

    def test_rising_star(self):
        ctx = self._make_ctx('Rising Star Game')
        assert determine_native_token(ctx, 'PIZZA') == 'STARBITS'

    def test_man_cave(self):
        ctx = self._make_ctx('The Man Cave')
        assert determine_native_token(ctx, 'PIZZA') == 'BRO'

    def test_ctp_talk(self):
        ctx = self._make_ctx('CTP Talk')
        assert determine_native_token(ctx, 'PIZZA') == 'CTP'

    def test_the_cartel(self):
        ctx = self._make_ctx('The Cartel')
        assert determine_native_token(ctx, 'PIZZA') == 'ONEUP'

    def test_unknown_guild(self):
        ctx = self._make_ctx('Some Other Server')
        assert determine_native_token(ctx, 'PIZZA') == 'PIZZA'


# ---------------------------------------------------------------------------
# get_coin_price
# ---------------------------------------------------------------------------

class TestGetCoinPrice:
    @patch('utils.CoinGeckoAPI')
    def test_success(self, mock_cg_cls):
        mock_cg = MagicMock()
        mock_cg_cls.return_value = mock_cg
        mock_cg.get_price.return_value = {
            'hive': {'usd': 0.35, 'usd_24h_change': 2.5, 'usd_24h_vol': 1000000}
        }
        price, change, vol = get_coin_price('hive')
        assert price == 0.35
        assert change == 2.5
        assert vol == 1000000

    @patch('utils.CoinGeckoAPI')
    def test_coin_not_in_response(self, mock_cg_cls):
        mock_cg = MagicMock()
        mock_cg_cls.return_value = mock_cg
        mock_cg.get_price.return_value = {}
        result = get_coin_price('fakecoin')
        assert result == (-1, -1, -1)

    @patch('utils.CoinGeckoAPI')
    def test_usd_not_in_subresponse(self, mock_cg_cls):
        mock_cg = MagicMock()
        mock_cg_cls.return_value = mock_cg
        mock_cg.get_price.return_value = {'hive': {}}
        result = get_coin_price('hive')
        assert result == (-1, -1, -1)

    @patch('utils.CoinGeckoAPI')
    def test_unbound_local_error(self, mock_cg_cls):
        mock_cg = MagicMock()
        mock_cg_cls.return_value = mock_cg
        mock_cg.get_price.side_effect = UnboundLocalError
        result = get_coin_price('hive')
        assert result == (-1, -1, -1)

    @patch('utils.CoinGeckoAPI')
    def test_default_coin_is_hive(self, mock_cg_cls):
        mock_cg = MagicMock()
        mock_cg_cls.return_value = mock_cg
        mock_cg.get_price.return_value = {
            'hive': {'usd': 0.30, 'usd_24h_change': 1.0, 'usd_24h_vol': 500000}
        }
        price, _, _ = get_coin_price()
        assert price == 0.30
        mock_cg.get_price.assert_called_once_with(
            ids='hive', vs_currencies='usd',
            include_24hr_change='true', include_24hr_vol='true')


# ---------------------------------------------------------------------------
# get_hive_internal_hbd_price
# ---------------------------------------------------------------------------

class TestGetHiveInternalHbdPrice:
    @patch('utils.get_hive_instance')
    def test_success(self, mock_get_hive):
        mock_hive = MagicMock()
        mock_get_hive.return_value = mock_hive
        mock_hive.get_median_price.return_value = 0.35

        mock_market = MagicMock()
        mock_market.ticker.return_value = {'latest': 2.857}  # ~2.857 HIVE per HBD

        with patch('beem.market.Market', return_value=mock_market):
            result = get_hive_internal_hbd_price()

        assert result is not None
        assert result['hbd_hive_price'] == 2.857
        assert result['feed_price'] == 0.35

    @patch('utils.get_hive_instance')
    def test_exception_returns_none(self, mock_get_hive):
        mock_get_hive.side_effect = Exception('node down')
        result = get_hive_internal_hbd_price()
        assert result is None


# ---------------------------------------------------------------------------
# get_token_price_he_cg — coin alias mapping
# ---------------------------------------------------------------------------

class TestGetTokenPriceHeCgAliases:
    """Verify coin shorthand aliases resolve correctly via the CoinGecko path."""

    def _patch_token_not_found(self):
        import hiveengine.exceptions
        return patch('utils.Token', side_effect=hiveengine.exceptions.TokenDoesNotExists)

    @patch('utils.get_coin_price')
    def test_eth_alias(self, mock_price):
        mock_price.return_value = (3000.0, 1.0, 9999999)
        with self._patch_token_not_found():
            embed = get_token_price_he_cg('ETH')
        assert 'ETHEREUM' in embed.title.upper()

    @patch('utils.get_coin_price')
    def test_btc_alias(self, mock_price):
        mock_price.return_value = (60000.0, 0.5, 99999999)
        with self._patch_token_not_found():
            embed = get_token_price_he_cg('BTC')
        assert 'BITCOIN' in embed.title.upper()

    @patch('utils.get_coin_price')
    def test_hbd_alias(self, mock_price):
        mock_price.return_value = (0.99, 0.1, 50000)
        with self._patch_token_not_found(), \
             patch('utils.get_hive_internal_hbd_price', return_value=None):
            embed = get_token_price_he_cg('HBD')
        assert 'HIVE_DOLLAR' in embed.title.upper()

    @patch('utils.get_coin_price')
    def test_matic_alias(self, mock_price):
        mock_price.return_value = (0.80, -1.0, 300000)
        with self._patch_token_not_found():
            embed = get_token_price_he_cg('matic')
        assert 'MATIC-NETWORK' in embed.title.upper()

    @patch('utils.get_coin_price')
    def test_polygon_alias(self, mock_price):
        mock_price.return_value = (0.80, -1.0, 300000)
        with self._patch_token_not_found():
            embed = get_token_price_he_cg('polygon')
        assert 'MATIC-NETWORK' in embed.title.upper()

    @patch('utils.get_coin_price')
    def test_cro_alias(self, mock_price):
        mock_price.return_value = (0.10, 0.2, 100000)
        with self._patch_token_not_found():
            embed = get_token_price_he_cg('cro')
        assert 'CRYPTO-COM-CHAIN' in embed.title.upper()


# ---------------------------------------------------------------------------
# get_token_price_he_cg — CoinGecko path
# ---------------------------------------------------------------------------

class TestGetTokenPriceCoinGecko:
    def _patch_token_not_found(self):
        import hiveengine.exceptions
        return patch('utils.Token', side_effect=hiveengine.exceptions.TokenDoesNotExists)

    @patch('utils.get_coin_price')
    def test_coingecko_embed_fields(self, mock_price):
        mock_price.return_value = (0.35, 2.5, 1000000)
        embed = get_token_price_he_cg('hive')
        assert 'CoinGecko' in embed.title
        assert '$0.35000' in embed.description

    @patch('utils.get_coin_price')
    def test_coin_not_found(self, mock_price):
        mock_price.return_value = (-1, -1, -1)
        with self._patch_token_not_found():
            embed = get_token_price_he_cg('fakecoin')
        assert 'Failed to find' in embed.description

    @patch('utils.get_hive_internal_hbd_price')
    @patch('utils.get_coin_price')
    def test_hbd_includes_internal_market(self, mock_price, mock_internal):
        mock_price.return_value = (0.99, 0.1, 50000)
        mock_internal.return_value = {
            'hbd_hive_price': 2.857,
            'feed_price': 0.35,
        }
        with self._patch_token_not_found():
            embed = get_token_price_he_cg('HBD')
        field_names = [f.name for f in embed.fields]
        assert 'Hive Internal Market' in field_names
        internal_field = next(f for f in embed.fields if f.name == 'Hive Internal Market')
        assert 'HBD price' in internal_field.value

    @patch('utils.get_hive_internal_hbd_price')
    @patch('utils.get_coin_price')
    def test_hbd_no_internal_when_none(self, mock_price, mock_internal):
        mock_price.return_value = (0.99, 0.1, 50000)
        mock_internal.return_value = None
        with self._patch_token_not_found():
            embed = get_token_price_he_cg('HBD')
        field_names = [f.name for f in embed.fields]
        assert 'Hive Internal Market' not in field_names


# ---------------------------------------------------------------------------
# get_token_price_he_cg — Hive-Engine path
# ---------------------------------------------------------------------------

class TestGetTokenPriceHiveEngine:
    @patch('utils.requests.get')
    @patch('utils.get_hiveengine_market_instance')
    @patch('utils.get_market_history')
    @patch('utils.get_coin_price')
    @patch('utils.Token')
    def test_hiveengine_token(self, mock_token, mock_price, mock_history,
                              mock_market, mock_requests):
        mock_token.return_value = MagicMock()  # Token exists
        mock_price.return_value = (0.35, 2.5, 1000000)
        mock_history.return_value = [{'price': '0.005'}]
        mock_market.get_sell_book.return_value = [{'price': '0.006'}]
        mock_market.get_buy_book.return_value = [{'price': '0.004'}]
        mock_requests.return_value.json.return_value = [
            {'volumeToken': '1000', 'symbol': 'PIZZA', 'volumeHive': '500'}
        ]

        embed = get_token_price_he_cg('PIZZA')
        assert 'Hive-Engine' in embed.title
        field_names = [f.name for f in embed.fields]
        assert 'Last' in field_names
        assert 'Ask' in field_names
        assert 'Bid' in field_names
        assert 'Today Volume' in field_names
