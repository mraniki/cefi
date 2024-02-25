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

    def __init__(
        self,
        protocol=None,
        name=None,
        user_id=None,
        api_key=None,
        host=None,
        port=None,
        broker_client_id=None,
        broker_account_number=None,
        broker_gateway=True,
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
    ):
        """
        Initialize the Cex object

        """
        self.protocol = protocol
        self.name = name
        self.client = None
        self.user_id = user_id
        self.api_key = api_key
        self.host = host
        self.port = port
        self.broker_client_id = broker_client_id
        self.broker_account_number = broker_account_number
        self.broker_gateway = broker_gateway
        self.secret = secret
        self.password = password
        self.testmode = testmode
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
