"""

Metatrader 5 client


"""

from mt5linux import MetaTrader5

from ._client import CexClient


class MetatraderHandler(CexClient):
    """
    library: https://github.com/lucas-campagna/mt5linux
    leveraging metatrder python integration:
    https://www.mql5.com/en/docs/integration/python_metatrader5/

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
        self.client = MetaTrader5(
            host=self.host or "localhost", port=self.port or 18812
        )
        self.client.initialize()
        self.client.terminal_info()

    async def get_quote(self, instrument):
        """
        Return a quote for a instrument


        Args:
            cex
            instrument

        Returns:
            quote
        """
        pass

    async def get_account_balance(self):
        """
        return account balance

        Args:
            None

        Returns:
            balance

        """

        return 0

    async def get_account_position(self):
        """
        Return account position.
        of a given exchange

        Args:
            None

        Returns:
            position

        """

        return 0

    async def get_trading_asset_balance(self):
        """ """
        return 0

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
        pass

    async def shutdown(self):
        self.client.shutdown()
