"""Tests for utils_hive.py."""
from unittest.mock import MagicMock, patch

from utils_hive import get_hive_power_delegations, get_hive_instance


class TestGetHivePowerDelegations:
    @patch('utils_hive.get_hive_instance')
    @patch('utils_hive.beem.account.Account')
    def test_sums_delegations(self, mock_account_cls, mock_get_hive):
        mock_hive = MagicMock()
        mock_get_hive.return_value = mock_hive
        mock_acc = MagicMock()
        mock_account_cls.return_value = mock_acc
        mock_acc.get_vesting_delegations.return_value = [
            {'vesting_shares': {'amount': '1000000', 'precision': 6}},
            {'vesting_shares': {'amount': '2000000', 'precision': 6}},
        ]
        mock_hive.vests_to_token_power.side_effect = [1000000, 2000000]

        result = get_hive_power_delegations('testwallet')
        assert result == 3.0  # (1000000 / 10^6) + (2000000 / 10^6)

    @patch('utils_hive.get_hive_instance')
    @patch('utils_hive.beem.account.Account')
    def test_no_delegations(self, mock_account_cls, mock_get_hive):
        mock_hive = MagicMock()
        mock_get_hive.return_value = mock_hive
        mock_acc = MagicMock()
        mock_account_cls.return_value = mock_acc
        mock_acc.get_vesting_delegations.return_value = []

        result = get_hive_power_delegations('testwallet')
        assert result == 0


class TestGetHiveInstance:
    def test_returns_hive(self):
        result = get_hive_instance()
        assert result is not None
