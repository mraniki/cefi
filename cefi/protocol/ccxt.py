"""

CCXT client


"""

import ccxt
from loguru import logger

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
        defaulttype="spot",
        ordertype="market",
        leverage_type="isolated",
        leverage=1,
        trading_risk_percentage=True,
        trading_risk_amount=1,
        trading_slippage=2,
        trading_amount_threshold=0,
        trading_asset="USDT",
        trading_asset_separator=None,
        mapping=None,
        **kwargs,
    ):
        """
        Initialize the ccxt client

        """

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
        self.account_number = self.client.uid
        self.name = self.client.id
        self.trading_asset = trading_asset
        self.separator = trading_asset_separator
        self.trading_risk_percentage = trading_risk_percentage
        self.trading_risk_amount = trading_risk_amount
        self.trading_slippage = trading_slippage
        self.trading_amount_threshold = trading_amount_threshold
        self.leverage_type = leverage_type
        self.leverage = leverage
        self.defaulttype = defaulttype
        self.ordertype = ordertype
        self.mapping = mapping

    async def get_quote(self, instrument):
        """
        Return a quote for a instrument
        of a given exchange ccxt object


        Args:
            cex
            instrument

        Returns:
            quote
        """
        try:
            instrument = await self.replace_instrument(instrument)

            ticker = self.client.fetch_ticker(instrument)
            quote = ticker["last"]
            logger.debug("Quote: {}", quote)
            return quote
        except Exception as e:
            logger.error("{} Error {}", self.name, e)

    async def get_account_balance(self):
        """
        return account balance of
        a given ccxt exchange

        Args:
            None

        Returns:
            balance

        """

        raw_balance = self.client.fetch_free_balance()
        if filtered_balance := {
            k: v for k, v in raw_balance.items() if v is not None and v > 0
        }:
            balance_str = "".join(
                f"{iterator}: {value} \n"
                for iterator, value in filtered_balance.items()
            )
            return f"{balance_str}"

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
            positions = self.client.fetch_positions()
            if positions := [p for p in positions if p["type"] == "open"]:
                return f"{positions}"
        except Exception as e:
            logger.error("{} Error {}", self.name, e)

    async def pre_order_checks(self, order_params):
        """ """
        return True

    async def get_trading_asset_balance(self):
        """ """
        return self.client.fetchBalance()[f"{self.trading_asset}"]["free"]

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
        try:
            action = order_params.get("action")
            instrument = await self.replace_instrument(order_params.get("instrument"))
            quantity = order_params.get("quantity", self.trading_risk_amount)
            logger.debug("quantity {}", quantity)
            amount = await self.get_order_amount(
                quantity=quantity,
                instrument=instrument,
                is_percentage=self.trading_risk_percentage,
            )
            params = {
                "stopLoss": {
                    "triggerPrice": order_params.get("stop_loss"),
                    # "price": order_params.get("action") * 0.98,
                },
                "takeProfit": {
                    "triggerPrice": order_params.get("take_profit"),
                    # "price": order_params.get("action") * 0.98,
                },
            }
            logger.debug("amount {}", amount)
            pre_order_checks = await self.pre_order_checks(order_params)
            logger.debug("pre_order_checks {}", pre_order_checks)

            if amount and pre_order_checks:
                if order := self.client.create_order(
                    symbol=instrument,
                    type=self.ordertype,
                    side=action,
                    amount=amount,
                    params=params,
                ):
                    return await self.get_trade_confirmation(order, instrument, action)
            return f"Error executing {self.name}"

        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return f"Error executing {self.name}"
