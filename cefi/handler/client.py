"""

CEX client based
class


"""

from loguru import logger


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

    def __init__(self, **kwargs):
        """
        Initialize the Cex object

        """

        try:
            self.protocol = kwargs.get("protocol", None)
            self.name = kwargs.get("name", None)
            logger.info("Initializing Client {}", self.name)
            self.enabled = kwargs.get("enabled", None)
            self.client = None
            self.user_id = kwargs.get("user_id", None)
            self.api_key = kwargs.get("api_key", None)
            self.host = kwargs.get("host", None)
            self.port = kwargs.get("port", None)
            self.broker_client_id = kwargs.get("broker_client_id", None)
            self.broker_account_number = kwargs.get("broker_account_number", None)
            self.broker_gateway = kwargs.get("broker_gateway", None)
            self.secret = kwargs.get("secret", None)
            self.password = kwargs.get("password", None)
            self.testmode = kwargs.get("testmode", None)
            self.trading_asset = kwargs.get("trading_asset", None)
            self.separator = kwargs.get("trading_asset_separator", None)
            self.account_number = None
            self.accounts_data = None
            self.trading_risk_percentage = kwargs.get("trading_risk_percentage", None)
            self.trading_risk_amount = kwargs.get("trading_risk_amount", None)
            self.trading_slippage = kwargs.get("trading_slippage", None)
            self.trading_amount_threshold = kwargs.get("trading_amount_threshold", None)
            self.leverage_type = kwargs.get("leverage_type", None)
            self.leverage = kwargs.get("leverage", None)
            self.defaulttype = kwargs.get("defaulttype", None)
            self.ordertype = kwargs.get("ordertype", None)
            self.mapping = kwargs.get("mapping", None)
            self.balance_limit = kwargs.get("balance_limit", True)
            self.balance_limit_value = kwargs.get("balance_limit_value", 10)

        except Exception as error:
            logger.error("Client initialization error {}", error)
            return None
        if not self.enabled:
            logger.debug("{} Not enabled", self.name)
            return

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
        """
        Return trading asset balance.

        Args:
            None

        Returns:
            balance

        """

    async def get_order_amount(self, quantity, instrument, is_percentage=True):
        """
        Calculate the order amount based on the risk percentage or money amount.

        Args:
            quantity: The quantity of the order.
            instrument: The instrument of the asset.
            is_percentage: True if quantity is a risk percentage,
            False if it is a money amount.

        Returns:
            The calculated order amount.

        """
        balance = await self.get_trading_asset_balance()
        logger.debug("Balance {}", balance)
        quote = await self.get_quote(instrument)
        logger.debug("Quote {}", quote)

        if not is_percentage and balance and quote:
            return quantity

        if balance and quote:
            risk_percentage = float(quantity) / 100
            amount = balance * risk_percentage / quote
            logger.debug("Amount {}", amount)
        if amount >= self.trading_amount_threshold:
            return amount

    async def pre_order_checks(self, order_params):
        """ """

    async def replace_instrument(self, instrument):
        """
        Replace instrument by an alternative instrument, if the
        instrument is not in the mapping, it will be ignored.

        Args:
            order (dict):

        Returns:
            dict
        """
        try:
            for item in self.mapping:
                if item["id"] == instrument:
                    instrument = item["alt"]
                    logger.debug(
                        "Instrument changed from {} to {}", item["id"], instrument
                    )
                    break

        except Exception as e:
            logger.error("{} Error {}", self.name, e)

        return instrument

    async def get_trade_confirmation(self, trade, instrument, action):
        """ """

        trade_confirmation = (
            f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
        )
        trade_confirmation += f"⚫ {round(0 or trade['amount'], 4)}\n"
        trade_confirmation += f"🔵 {round(0 or trade['price'], 4)}\n"
        trade_confirmation += f"🟢 {round(0 or trade['takeProfitPrice'], 4)}\n"
        trade_confirmation += f"🔴 {round(0 or trade['stopLossPrice'], 4)}\n"
        trade_confirmation += f"ℹ️ {trade['id']}\n"
        trade_confirmation += f"🗓️ {trade['datetime']}"
        if trade_confirmation:
            return f"{self.name}:\n{trade_confirmation}"
