"""Tests for utils_hiveengine.py."""
from unittest.mock import MagicMock, patch

from utils_hiveengine import (
    get_market_history,
    get_token_holders,
    get_hiveengine_instance,
    get_hiveengine_market_instance,
)


class TestGetMarketHistory:
    def test_single_page(self):
        mock_market = MagicMock()
        mock_market.get_trades_history.return_value = [
            {'price': '0.01'}, {'price': '0.02'}
        ]
        result = get_market_history('PIZZA', market=mock_market)
        assert len(result) == 2
        mock_market.get_trades_history.assert_called_once_with('PIZZA', limit=1000, offset=0)

    def test_multi_page(self):
        mock_market = MagicMock()
        page1 = [{'price': str(i)} for i in range(1000)]
        page2 = [{'price': '999'}]
        mock_market.get_trades_history.side_effect = [page1, page2]

        result = get_market_history('PIZZA', market=mock_market)
        assert len(result) == 1001
        assert mock_market.get_trades_history.call_count == 2

    def test_empty(self):
        mock_market = MagicMock()
        mock_market.get_trades_history.return_value = []
        result = get_market_history('PIZZA', market=mock_market)
        assert result == []


class TestGetTokenHolders:
    @patch('utils_hiveengine.Token')
    @patch('utils_hiveengine.get_hiveengine_instance')
    def test_single_page(self, mock_get_api, mock_token_cls):
        mock_token = MagicMock()
        mock_token_cls.return_value = mock_token
        mock_token.get_holder.return_value = [
            {'account': 'user1', 'balance': '100'},
            {'account': 'user2', 'balance': '200'},
        ]
        result = get_token_holders('PIZZA')
        assert len(result) == 2

    @patch('utils_hiveengine.Token')
    @patch('utils_hiveengine.get_hiveengine_instance')
    def test_multi_page(self, mock_get_api, mock_token_cls):
        mock_token = MagicMock()
        mock_token_cls.return_value = mock_token
        page1 = [{'account': f'user{i}'} for i in range(1000)]
        page2 = [{'account': 'userlast'}]
        mock_token.get_holder.side_effect = [page1, page2]

        result = get_token_holders('PIZZA')
        assert len(result) == 1001


class TestGetInstances:
    def test_hiveengine_instance(self):
        assert get_hiveengine_instance() is not None

    def test_market_instance(self):
        assert get_hiveengine_market_instance() is not None
