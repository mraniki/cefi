"""

Oanda client


"""

from easyoanda import easyoanda
from loguru import logger

from ._client import CexClient


class OandaHandler(CexClient):
    """
    library: https://pypi.org/project/easyoanda/

    Args:
        None

    Returns:
        None

    """

    def __init__(
        self,
        **kwargs,
    ):
        """
        Initialize the client

        """
        super().__init__(**kwargs)
        self.client = easyoanda.start_session(
            sessionType="paper",
            accountID=self.user_id,
            token=self.api_key,
        )

    async def get_quote(self, instrument):
        """
        Return a quote for a instrument


        Args:
            cex
            instrument

        Returns:
            quote
        """
        if quotes := self.client.pricing.start_stream(instrument):
            quote = quotes[0]
            return quote["bids"][0]["price"]

    async def get_account_balance(self):
        """
        return account balance

        Args:
            None

        Returns:
            balance

        """
        self.accounts_data = self.client.account.get_summary()
        return self.accounts_data["account"]["balance"]

    async def get_account_position(self):
        """
        Return account position.
        of a given exchange

        Args:
            None

        Returns:
            position

        """

        position_data = self.client.positions.openPositions()
        return position_data["positions"]

    async def get_trading_asset_balance(self):
        """ """
        self.accounts_data = self.client.account.get_summary()
        return self.accounts_data["account"]["balance"]

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
        instrument = await self.replace_instrument(order_params.get("instrument"))
        quantity = order_params.get("quantity", self.trading_risk_amount)
        if not action or not instrument:
            raise ValueError("Missing required parameters: action or instrument")
        logger.debug(f"quantity {quantity}")
        amount = await self.get_order_amount(
            quantity=quantity,
            instrument=instrument,
            is_percentage=self.trading_risk_percentage,
        )
        if not amount:
            raise ValueError("Failed to calculate order amount")
        logger.debug(f"amount {amount}")
        pre_order_checks = await self.pre_order_checks(order_params)
        if not pre_order_checks:
            raise ValueError("Pre-order checks failed")

        if action == "SELL":
            amount = -amount

        marketOrder = easyoanda.MarketOrder()
        marketOrder.set(instrument=instrument, units=amount)
        self.client.orders.place_order(marketOrder)
