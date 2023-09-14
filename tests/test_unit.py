from datetime import datetime
from unittest.mock import AsyncMock

import ccxt
import pytest

from cefi import CexTrader
from cefi.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_CEX():
    settings.configure(FORCE_ENV_FOR_DYNACONF="cex")


@pytest.fixture(name="order_parsed")
def result_order():
    """return standard expected results"""
    return {
        "action": "BUY",
        "instrument": "BTCUSDT",
        "stop_loss": 200,
        "take_profit": 400,
        "quantity": 2,
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
    assert settings.VALUE == "On Testing CEX_binance"


@pytest.mark.asyncio
async def test_cefi(CXTrader):
    print(type(CXTrader))
    result = await CXTrader.get_info()
    assert "🪪" in result
    assert "💱 binance" in result
    assert CXTrader is not None
    assert isinstance(CXTrader, CexTrader)
    assert callable(CXTrader.get_account_balance)
    assert callable(CXTrader.get_account_position)
    assert callable(CXTrader.execute_order)


@pytest.mark.asyncio
async def test_help(CXTrader):
    """Test help"""

    result = await CXTrader.get_help()
    assert result is not None
    assert "🎯" in result
    assert "🏦" in result


@pytest.mark.asyncio
async def test_quote(CXTrader, caplog):
    """Test quote"""
    result = await CXTrader.get_quotes("BTCUSDT")
    assert result is not None
    assert "🏦" in result
    assert result is not None


@pytest.mark.asyncio
async def test_balance(CXTrader):
    """Test balance"""
    result = await CXTrader.get_account_balances()
    assert result is not None
    assert "🏦" in result


@pytest.mark.asyncio
async def test_position(CXTrader):
    result = await CXTrader.get_account_positions()
    assert "📊 Position" in result


@pytest.mark.asyncio
async def test_position_error(CXTrader, caplog):
    """Test position"""
    CXTrader.get_account_positions = AsyncMock()
    await CXTrader.get_account_positions("/pos")
    CXTrader.get_account_positions.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_account_pnl(CXTrader):
    """Test pnl"""

    result = await CXTrader.get_account_pnl()
    assert result == 0


@pytest.mark.asyncio
async def test_execute_order(CXTrader, order_parsed):
    """Test order"""
    result = await CXTrader.execute_order(order_parsed)
    print(result)
    assert result is not None
    assert any("binance" in item for item in result)
    # assert ("⬆️" in result) or ("⬇️" in result)
    # assert "ℹ️" in result
