"""

CEX client based
class


"""

from loguru import logger

from cefi.config import settings


class CexClient:
    """
    CEX Object to support CEFI
    exchange and trading
    via CCXT library
    https://github.com/ccxt/ccxt

    Args:
        None

    Returns:
        None

    """

    def __init__(self):
        """
        Initialize the Cex object

        """

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

    async def get_account_balance(self):
        """
        return account balance of
        a given ccxt exchange

        Args:
            None

        Returns:
            balance

        """

    async def get_account_position(self):
        """
        Return account position.
        of a given exchange

        Args:
            None

        Returns:
            position

        """

    async def get_account_pnl(self):
        """
        Return account pnl.

        Args:
            None

        Returns:
            pnl
        """

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

    async def get_trading_asset_balance(self):
        """ """

    async def get_order_amount(self, quantity, symbol):
        """
        Return amount based on risk percentage.

        Args:
            quantity
            symbol

        Returns:
            amount

        """
        logger.debug("quantity: {}", quantity)
        logger.debug("symbol: {}", symbol)
        balance = await self.get_trading_asset_balance
        quote = await self.get_quote(symbol)
        if balance and quote:
            return balance * (float(quantity) / 100) / quote

    async def pre_order_checks(self, order_params):
        """ """
        pass
        # if await self.get_account_balance() == "No Balance":
        #     return f"{self.name}:\nNo Funding"

        # asset_out_quote = await self.get_quote(instrument)
        # if asset_out_quote == "No Quote":
        #     return f"{self.name}:\nNo quote"

        # asset_out_balance = self.client.fetchBalance()[f"{trading_asset}"]["free"]

        # if not asset_out_balance:
        #     return f"{self.name}:\nNo Funding"

    async def get_trade_confirmation(self, trade, instrument, action):
        """ """

        trade_confirmation = (
            f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
        )
        trade_confirmation += f"⚫ {round(trade['amount'], 4)}\n"
        trade_confirmation += f"🔵 {round(trade['price'], 4)}\n"
        trade_confirmation += f"🟢 {round(trade['price'], 4)}\n"
        trade_confirmation += f"🔴 {round(trade['price'], 4)}\n"
        trade_confirmation += f"ℹ️ {trade['id']}\n"
        trade_confirmation += f"🗓️ {trade['datetime']}"
        if trade_confirmation:
            return f"{self.name}:\n{trade_confirmation}"

    async def replace_instrument(self, instrument):
        """
        Replace instrument by an alternative instrument, if the
        instrument is not in the mapping, it will be ignored.

        Args:
            order (dict):

        Returns:
            dict
        """
        for item in self.mapping:
            if item["id"] == instrument:
                instrument = item["alt"]
                self.logger.debug("Instrument symbol changed", instrument)
                break

        return instrument
