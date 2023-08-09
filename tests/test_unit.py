"""
FindMyOrder Unit Testing
"""

from datetime import datetime

import pytest

from findmyorder import FindMyOrder, settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    

@pytest.fixture(name="fmo")
def fmo():
    """return fmo"""
    return FindMyOrder()

@pytest.fixture
def order():
    """return valid order"""
    return "buy EURUSD sl=200 tp=400 q=2%"

@pytest.fixture
def short_order():
    """return valid order"""
    return "Buy EURUSD"

@pytest.fixture
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
        "timestamp": datetime.now()
    }

@pytest.fixture
def ignore_order():
    """return valid order"""
    return "buy US500"

@pytest.fixture
def crypto_order():
    """return valid order"""
    return "SHORT ETH sl=200 tp=400 q=2%"

@pytest.fixture
def crypto_short_order():
    """return valid order"""
    return "Sell ETH"

@pytest.fixture
def result_crypto_order():
    """return standard expected results"""
    return {
        "action": "SHORT",
        "instrument": "WETH",
        "stop_loss": 1000,
        "take_profit": 1000,
        "quantity": 10,
        "order_type": None,
        "leverage_type": None,
        "comment": None,
        "timestamp": datetime.now()
        }

@pytest.fixture
def order_with_emoji():
    """return emoji type order"""
    return """⚡️⚡️ #BNB/USDT ⚡️⚡️
    Exchanges: ByBit USDT, Binance Futures
    Signal Type: Regular (Long)
    Leverage: Cross (20.0X)"""


@pytest.fixture
def bot_command():
    return "/bal"


@pytest.fixture
def invalid_order():
    """return fmo"""
    return "This is not an order"

@pytest.mark.asyncio
async def test_settings():
    """Search Testing"""
    assert settings.VALUE == "On Testing"
    assert settings.findmyorder_enabled is True


@pytest.mark.asyncio
async def test_info(fmo):
    """Search Testing"""
    result = await fmo.get_info()
    print(result)
    assert result is not None
    assert str(result).startswith("FindMyOrder")

@pytest.mark.asyncio
async def test_search_valid_order(fmo, crypto_order):
    """Search Testing"""
    assert await fmo.search(crypto_order) is True


@pytest.mark.asyncio
async def test_search_no_order(fmo, invalid_order):
    """Search Testing"""
    assert await fmo.search(invalid_order) is False


@pytest.mark.asyncio
async def test_search_no_order_command(fmo, bot_command):
    """Search Testing"""
    assert await fmo.search(bot_command) is False


@pytest.mark.asyncio
async def test_search_exception(fmo):
    """Search Testing"""
    mystring = ""
    assert await fmo.search(mystring) is False


@pytest.mark.asyncio
async def test_search_normal_order(fmo,order):
    """Search Testing"""
    assert await fmo.search(order) is True


@pytest.mark.asyncio
async def test_search_normal_order_variation(fmo,crypto_order):
    """Search Testing"""
    assert await fmo.search(crypto_order) is True


@pytest.mark.asyncio
async def test_identify_order(fmo, short_order):
    """Identify Testing"""
    result = await fmo.identify_order(short_order)
    assert result is not None


@pytest.mark.asyncio
async def test_identify_order_invalid_input(fmo, invalid_order):
    """Identify Testing"""
    result = await fmo.identify_order(invalid_order)
    assert str(result).startswith("Expected")



@pytest.mark.asyncio
async def test_valid_get_order(fmo, order, result_order):
    """get order Testing"""
    result = await fmo.get_order(order)
    assert result["action"] == result_order["action"]
    assert result["instrument"] == result_order["instrument"]
    assert int(result["stop_loss"]) == result_order["stop_loss"]
    assert int(result["take_profit"]) == result_order["take_profit"]
    assert int(result["quantity"]) == result_order["quantity"]
    assert result["order_type"] == result_order["order_type"]
    assert result["leverage_type"] == result_order["leverage_type"]
    assert result["comment"] == result_order["comment"]
    assert type(result["timestamp"] is datetime)


@pytest.mark.asyncio
async def test_short_valid_get_order(fmo, short_order, result_order):
    """get order Testing"""
    result = await fmo.get_order(short_order)
    assert result["action"] == result_order["action"]
    assert result["instrument"] == result_order["instrument"]
    assert int(result["quantity"]) == 1
    assert type(result["timestamp"] is datetime)


@pytest.mark.asyncio
async def test_ignore_order(fmo, ignore_order):
    """ignore order Testing"""
    result = await fmo.get_order(ignore_order)
    assert result is None


@pytest.mark.asyncio
async def test_invalid_get_order(fmo, invalid_order):
    """ignore order Testing"""
    result = await fmo.get_order(invalid_order)
    assert result is None


@pytest.mark.asyncio
async def test_mapping_order(
    fmo,
    crypto_short_order,
    result_crypto_order):
    """replace instrument Testing"""
    result = await fmo.get_order(crypto_short_order)
    print(result)
    assert settings.instrument_mapping is True
    assert result["instrument"] == result_crypto_order["instrument"]
    assert type(result["timestamp"] is datetime)


@pytest.mark.asyncio
async def test_contains_no_emoji(fmo, order):
    """check emoji"""
    result = await fmo.contains_emoji(order)
    assert result is False


@pytest.mark.asyncio
async def test_contains_emoji(fmo,order_with_emoji):
    """check emoji"""
    result = await fmo.contains_emoji(order_with_emoji)
    assert result is True

