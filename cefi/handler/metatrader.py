"""

Metatrader 5 client


"""

from loguru import logger
from mt5linux_updated import MetaTrader5 as mt5

from ._client import CexClient


class MetatraderHandler(CexClient):
    """
    library: https://github.com/lucas-campagna/mt5linux
    leveraging metatrader python integration:
    https://www.mql5.com/en/docs/integration/python_metatrader5/

    You can use MT5 via the docker image
    gmag11/metatrader5_vnc which include the python integration
    if your metatrader container is named metatrader5
    and the python port is 8001 it will connect

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
        self.client = mt5(host=self.host or "metatrader5", port=self.port or 8001)
        if not self.client.initialize():
            logger.error("initialize() failed")
            mt5.shutdown()
        logger.info(
            "MT5 initialized\n{}\n{}",
            self.client.terminal_info(),
            self.client.version(),
        )

    async def get_account_info(self):
        """
        Returns:
            str
        """
        self.accounts_data = self.client.get_account_info()
        return self.accounts_data

    async def shutdown(self):
        self.client.shutdown()

    async def get_account_balance(self):
        """
        return account balance

        Args:
            None

        Returns:
            balance

        """
        if account_info := self.get_account_info():
            return account_info.balance

    async def get_trading_asset_balance(self):
        """ """
        return self.get_account_balance()

    async def get_account_free_margin(self):
        """
        return account balance

        Args:
            None

        Returns:
            balance

        """
        if account_info := self.get_account_info():
            return account_info.margin_free

    async def get_account_position(self):
        """
        Return account position.
        of a given exchange

        Args:
            None

        Returns:
            position

        """
        if account_info := self.get_account_info():
            currency = account_info.currency
            if positions := self.client.positions():
                return [f"{p.symbol} {p.profit} {currency}" for p in positions if p]
        else:
            return []

    async def get_quote(self, instrument):
        """
        Return a quote for a instrument


        Args:
            cex
            instrument

        Returns:
            quote
        """
        if not instrument:
            raise ValueError("instrument cannot be empty")
        if quote := self.client.symbol_info_tick(instrument):
            return quote.bid
        else:
            raise ValueError("quote is empty")

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
        # TODO: implement

    async def calculate_pnl(self, from_date, to_date):
        """
        Calculate the PnL for a given start date.

        Parameters:
            from_date: The start date for which to calculate PnL.
            to_date: The end date for which to calculate PnL.

        Returns:
            pnl: The calculated PnL value.
        """
        return self.client.history_orders_get(from_date, to_date)
