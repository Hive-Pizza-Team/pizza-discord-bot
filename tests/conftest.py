"""Shared fixtures for pizza-discord-bot tests."""
import sys
import types
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Stub heavy third-party modules so we can import project code without
# connecting to any blockchain node or external API at import time.
# ---------------------------------------------------------------------------

def _install_stubs():
    """Insert lightweight stubs for beem / hiveengine / pycoingecko into sys.modules."""

    # -- beem --
    beem_mod = types.ModuleType("beem")
    beem_mod.Hive = MagicMock
    beem_mod.account = MagicMock()
    beem_mod.instance = MagicMock()
    sys.modules["beem"] = beem_mod
    sys.modules["beem.witness"] = types.ModuleType("beem.witness")
    sys.modules["beem.witness"].Witness = MagicMock
    sys.modules["beem.witness"].WitnessesRankedByVote = MagicMock
    sys.modules["beem.market"] = types.ModuleType("beem.market")
    sys.modules["beem.market"].Market = MagicMock
    sys.modules["beem.instance"] = beem_mod.instance
    sys.modules["beem.account"] = beem_mod.account

    # -- hiveengine --
    he_mod = types.ModuleType("hiveengine")
    he_exceptions = types.ModuleType("hiveengine.exceptions")

    class TokenDoesNotExists(Exception):
        pass

    he_exceptions.TokenDoesNotExists = TokenDoesNotExists
    he_mod.exceptions = he_exceptions
    sys.modules["hiveengine"] = he_mod
    sys.modules["hiveengine.exceptions"] = he_exceptions
    sys.modules["hiveengine.api"] = types.ModuleType("hiveengine.api")
    sys.modules["hiveengine.api"].Api = MagicMock
    sys.modules["hiveengine.market"] = types.ModuleType("hiveengine.market")
    sys.modules["hiveengine.market"].Market = MagicMock
    sys.modules["hiveengine.tokenobject"] = types.ModuleType("hiveengine.tokenobject")
    sys.modules["hiveengine.tokenobject"].Token = MagicMock
    sys.modules["hiveengine.wallet"] = types.ModuleType("hiveengine.wallet")
    sys.modules["hiveengine.wallet"].Wallet = MagicMock

    # -- pycoingecko --
    cg_mod = types.ModuleType("pycoingecko")
    cg_mod.CoinGeckoAPI = MagicMock
    sys.modules["pycoingecko"] = cg_mod

    # -- dotenv --
    dotenv_mod = types.ModuleType("dotenv")
    dotenv_mod.load_dotenv = lambda *a, **kw: None
    sys.modules["dotenv"] = dotenv_mod


_install_stubs()
