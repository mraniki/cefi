from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cefi import CexTrader
from cefi.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_CEX():
    settings.configure(FORCE_ENV_FOR_DYNACONF="cefi")


@pytest.fixture(name="order_parsed")
def result_order():
    """return standard expected results"""
    return {
        "action": "BUY",
        "instrument": "BTCUSDT",
        "stop_loss": 2000,
        "take_profit": 400,
        "quantity": 1,
        "order_type": None,
        "leverage_type": None,
        "comment": None,
        "timestamp": datetime.now(),
    }


@pytest.fixture(name="CXTrader")
def test_fixture():
    return CexTrader()


def test_dynaconf_is_in_testing_env_CEX():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing CEX"


@pytest.mark.asyncio
async def test_cefi(CXTrader):
    print(type(CXTrader))
    result = await CXTrader.get_info()
    assert "🪪" in result
    assert "💱 binance" in result
    assert CXTrader is not None
    assert isinstance(CXTrader, CexTrader)
    assert callable(CXTrader.get_balances)
    assert callable(CXTrader.get_positions)
    #assert callable(CXTrader.execute_order)


# @pytest.mark.asyncio
# async def test_help(CXTrader):
#     """Test help"""

#     result = await CXTrader.get_help()
#     assert result is not None
#     assert "🎯" in result
#     assert "🏦" in result


@pytest.mark.asyncio
async def test_quote(CXTrader, caplog):
    """Test quote"""
    result = await CXTrader.get_quotes("BTC")
    assert result is not None
    assert "🏦" in result
    assert ("binance" in result) or ("huobi" in result)
    assert ("No Quote" in result) or ("2" in result)


@pytest.mark.asyncio
async def test_get_balances(CXTrader):
    """Test balance"""
    result = await CXTrader.get_balances()
    assert result is not None
    assert "🏦" in result
    assert ("binance" in result) or ("huobi" in result)


@pytest.mark.asyncio
async def test_get_positions(CXTrader):
    result = await CXTrader.get_positions()
    assert "📊 Position" in result


@pytest.mark.asyncio
async def test_get_pnls(CXTrader):
    """Test pnl"""

    result = await CXTrader.get_pnls()
    assert "0" in result


@pytest.mark.asyncio
async def test_submit_order(CXTrader, order_parsed):
    result = await CXTrader.submit_order(order_parsed)
    assert result is not None
    assert "binance" in result[0]
    assert "huobi" in result[1]
    assert "🔵" in result[0]
    assert "🔴" in result[0]
    assert "ℹ️" in result[0]
    assert "🗓️" in result[0]
    assert "No quote" in result[1]
