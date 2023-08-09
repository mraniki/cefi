from datetime import datetime
from unittest.mock import AsyncMock

import ccxt
import pytest

from cex import CexExchange
from cex.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_CEX():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testingbinancecex")


@pytest.fixture(name="order_message")
def order():
    """return valid order"""
    return "buy BTCUSDT sl=200 tp=400 q=1%"


@pytest.fixture(name="order_parsed")
def result_order():
    """return standard expected results"""
    return {
        "action": "BUY",
        "instrument": "EURUSD",
        "stop_loss": 200,
        "take_profit": 400,
        "quantity": 2,
        "order_type": None,
        "leverage_type": None,
        "comment": None,
        "timestamp": datetime.now(),
    }


@pytest.fixture(name="exchange")
def test_fixture_plugin():
    return CexExchange()


def test_dynaconf_is_in_testing_env_CEX():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing CEX_binance"
    assert settings.cex_name == "binance"


@pytest.mark.asyncio
async def test_plugin(exchange):
    print(type(exchange))
    result = await exchange.get_info()
    assert "🪪" in result
    assert "💱 binance" in result
    assert exchange is not None
    assert isinstance(exchange, ccxt.Binance)
    assert callable(exchange.get_account_balance)
    assert callable(exchange.get_account_position)
    assert callable(exchange.execute_order)


@pytest.mark.asyncio
async def test_position(exchange):
    with pytest.raises(Exception):
        await exchange.get_account_position()
        # assert "📊 Position" in result


@pytest.mark.asyncio
async def test_parse_quote(exchange, caplog):
    """Test parse_message balance"""
    await exchange.get_quote("/q BTCUSDT")
    assert "🏦" in caplog.text


@pytest.mark.asyncio
async def test_parse_help(exchange):
    """Test help"""
    exchange.get_help = AsyncMock()
    await exchange.get_help()
    exchange.get_help.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_info(exchange):
    """Test info"""
    exchange.get_info = AsyncMock()
    await exchange.get_info()
    exchange.get_info.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_balance(exchange):
    """Test balance"""
    with pytest.raises(Exception):
        exchange.assert_awaited_once = AsyncMock()
        await exchange.get_account_balance("/bal")
        exchange.get_account_balance.assert_called()


@pytest.mark.asyncio
async def test_parse_position(exchange, caplog):
    """Test position"""
    exchange.get_account_position = AsyncMock()
    await exchange.get_account_position("/pos")
    exchange.get_account_position.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_account_pnl(exchange):
    """Test pnl"""
    exchange.get_account_pnl = AsyncMock()
    await exchange.get_account_pnl("/d")
    exchange.get_account_pnl.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_help(exchange):
    result = await exchange.get_help()
    print(result)
    assert result is not None
    assert "🎯" in result
    assert "🏦" in result


@pytest.mark.asyncio
async def test_execute_order(exchange, order_parsed):
    result = await exchange.execute_order(order_parsed)
    print(result)
    assert result is not None
    assert "⚠️ order execution" in result


# @pytest.mark.asyncio
# async def test_cex_exchange():
#     exchange_instance = CexExchange()
#     ccxt_client_mock = AsyncMock()
#     ccxt_client_mock.uid = '12345'
#     ccxt_client_mock.fetchTicker.side_effect = lambda symbol: {'last': 5000}
#     ccxt_client_mock.fetchBalance = AsyncMock(return_value={'BTC': {'free': 1}})
#     ccxt_client_mock.create_order = AsyncMock(
#         return_value={
#             'id': '12345',
#             'amount': 1,
#             'price': 5000,
#             'datetime': '2022-01-01 00:00:00'})
#     exchange_instance.cex = ccxt_client_mock

#     with patch('ccxt.binance', return_value=ccxt_client_mock):

#         result = await exchange_instance.get_info()

#         assert result is not None
#         assert '💱' in result
#         assert '🪪' in result

#         order_params = {
#             'action': 'BUY',
#             'instrument': 'BTCUSDT',
#             'quantity': 100
#         }

#         result = await ccxt_client_mock.execute_order(order_params)
#         print(result)
#         assert result is not None
#         assert '⬆️ BTC/USD' in result

#         ccxt_client_mock.fetchTicker.assert_awaited_once_with('BTCUSDT')
#         ccxt_client_mock.fetchBalance.assert_awaited_once()
#         ccxt_client_mock.create_order.assert_awaited_once_with(
#             'BTCUSDT', settings.cex_ordertype, 'BUY', 0.02, price=None)
