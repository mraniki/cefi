from datetime import datetime
from unittest.mock import AsyncMock

import ccxt
import pytest

from cefi import CexExchange
from cefi.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_CEX():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testingbinancecex")


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

 
@pytest.fixture(name="exchange")
def test_fixture():
    return CexExchange()


def test_dynaconf_is_in_testing_env_CEX():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing CEX_binance"
    assert settings.cex_name == "binance"


@pytest.mark.asyncio
async def test_cefi(exchange):
    print(type(exchange))
    result = await exchange.get_info()
    assert "🪪" in result
    assert "💱 binance" in result
    assert exchange is not None
    assert isinstance(exchange, CexExchange)
    assert callable(exchange.get_account_balance)
    assert callable(exchange.get_account_position)
    assert callable(exchange.execute_order)


@pytest.mark.asyncio
async def test_help(exchange):
    """Test help"""

    result = await exchange.get_help()
    exchange.get_help.assert_awaited_once()
    assert result is not None
    assert "🎯" in result
    assert "🏦" in result


@pytest.mark.asyncio
async def test_balance(exchange):
    """Test balance"""
    result = await exchange.get_account_balance()
    assert result is not None
    assert "USDT" in result


# @pytest.mark.asyncio
# async def test_position(exchange):
#     #with pytest.raises(Exception):
#     result = await exchange.get_account_position()
#     assert "📊 Position" in result


@pytest.mark.asyncio
async def test_position_error(exchange, caplog):
    """Test position"""
    exchange.get_account_position = AsyncMock()
    await exchange.get_account_position("/pos")
    exchange.get_account_position.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_account_pnl(exchange):
    """Test pnl"""

    result = await exchange.get_account_pnl()
    exchange.get_account_pnl.assert_awaited_once()
    assert result == 0


@pytest.mark.asyncio
async def test_quote(exchange, caplog):
    """Test quote"""
    result = await exchange.get_quote("BTCUSDT")
    assert result is not None
    assert "🏦" in result
    assert "BTCUSDT" in result


@pytest.mark.asyncio
async def test_execute_order(exchange, order_parsed):
    result = await exchange.execute_order(order_parsed)
    print(result)
    assert result is not None
    assert "⬆️" in result
    assert "ℹ️" in result
    #assert "⚠️ order execution" in result


