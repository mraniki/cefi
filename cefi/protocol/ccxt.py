"""

CCXT client


"""

import ccxt
from loguru import logger

from cefi.config import settings

from .client import CexClient


class CexCcxt(CexClient):
    """
    CEX client 
    via CCXT library
    https://github.com/ccxt/ccxt

    Args:
        None

    Returns:
        None

    """

    def __init__(
        self,
        protocol="ccxt",
        name=None,
        api_key=None,
        secret=None,
        password=None,
        testmode=True,
        defaultype="spot",
        ordertype="market",
        trading_risk_amount=1,
        trading_asset="USDT",
        trading_asset_separator=None,
        mapping=None,
        )
        """
        Initialize the ccxt client

        """


        try:
            logger.debug(f"Loading {exchange}")
            client = getattr(ccxt, name)
            self.client = client(
                    {
                        "apiKey": api_key,
                        "secret": secret,
                        "password": password,
                        "enableRateLimit": True,
                        "options": {
                            "defaultType": defaulttype,
                        },
                    }
                )
            if testmode:
            self.client.set_sandbox_mode("enabled")
            self.account = cx_client.uid
            self.name = cx_client.id
            self.trading_asset = trading_asset
            self.separator = trading_asset_separator
            self.trading_risk_amount = trading_risk_amount
            self.exchange_defaulttype = defaulttype
            self.exchange_ordertype = ordertype
        except Exception as e:
            logger.error("CexCcxt init: {}", e)


    async def get_quote(self, symbol):
        """
        Return a quote for a symbol
        of a given exchange ccxt object


        Args:
            cex
            symbol

        Returns:
            quote
        """
        try:
            ticker = selfclient.fetch_ticker(symbol)
            logger.debug("ticker: {}", ticker)
            return ticker["last"]
        except Exception as e:
            logger.error("get_quote: {}", e)
            return "No Quote"


    async def get_account_balance(self):
        """
        return account balance of
        a given ccxt exchange

        Args:
            None

        Returns:
            balance

        """
        try:
            raw_balance = self.client.fetch_free_balance()
            if filtered_balance := {
                k: v for k, v in raw_balance.items() if v is not None and v > 0
            }:
                balance_str = "".join(
                    f"{iterator}: {value} \n"
                    for iterator, value in filtered_balance.items()
                )
                return f"{balance_str}"
        except Exception as e:
            logger.error(e)
            return "No Balance"


    async def get_account_position(self):
        """
        Return account position.
        of a given exchange

        Args:
            None

        Returns:
            position

        """
        try:
            positions = cx_client.fetch_positions()
            if positions := [p for p in positions if p["type"] == "open"]:
                return f"{positions}"
        except Exception as e:
            logger.error(e)
            return "No Position"


    async def execute_order(self, order_params):
        """
        Execute order

        Args:
            order_params (dict):
                action(str)
                instrument(str)
                quantity(int)

        Returns:
            trade_confirmation(dict)

        """
        action = order_params.get("action")
        instrument = await replace_instrument(order_params.get("instrument"))
        quantity = order_params.get("quantity", self.trading_risk_amount)
        
        try:
            if await order_checks():
                amount = (
                asset_out_balance * (float(quantity) / 100) / asset_out_quote
            )

                trade = cx_client.create_order(
                instrument,
                self.order_type,
                action,
                amount,
                # price=None
            )

                if not trade:
                return (f"Error executing {self.name}")
                return await self.get_trade_confirmation(trade, action, instrument)

        except Exception as e:
            logger.debug("{} Error {}", self.name, e)
            return (f"Error executing {self.name}")


