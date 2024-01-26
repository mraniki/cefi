"""

Interactive Brokers client


"""

from ib_insync import IB, Forex, Order
from loguru import logger

from cefi.config import settings

from .client import CexClient


class CexIB(CexClient):
    """
    CEX client for IBKR


    Args:
        None

    Returns:
        None

    """

    def __init__(
        self,
        protocol="ib",
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
        Initializes the Broker_IBKR_Plugin class.

        This function creates an instance of the IB class from the ib_insync
        library and sets it as the 'ib' attribute of the class.
        It also sets the 'client' attribute to None as a placeholder
        for actual client details.

        To connect to the Interactive Brokers (IBKR) platform,
        the 'connect' method of the 'ib' instance is called.
        This method requires the host, port, and clientId as parameters.
        In this case, the function connects to the IBKR platform using
        the IP address "127.0.0.1", port 7497, and clientId 1.

        After successfully connecting to IBKR, the function logs
        a debug message using the logger module.

        """

        # client = getattr(ccxt, name)
        # self.client = client(
        #     {
        #         "apiKey": api_key,
        #         "secret": secret,
        #         "password": password,
        #         "enableRateLimit": True,
        #         "options": {
        #             "defaultType": defaulttype,
        #         },
        #     }
        # )
        # if testmode:
        #     self.client.set_sandbox_mode("enabled")

        self.client = IB()
        self.client.connect(
            host=settings.broker_host or "127.0.0.1",
            port=settings.broker_port or 7497,
            clientId=settings.broker_clientId or 1,
            readonly=settings.broker_read_only or False,
            account=settings.broker_account_number or "",
        )
        logger.debug("Connected to IBKR {}", self.client.isConnected())
        self.name = self.client.id
        self.account_number = self.client.managedAccounts()[0]
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
        logger.debug("Broker_IBKR_Plugin initialized with account: {}", self.account)

    async def get_info(self):
        """
        Retrieves information from the accountValues method of the `ib` object.

        Returns:
            The result of calling the accountValues method of the `ib` object.
        """
        return self.client.accountValues()

    async def get_quote(self, instrument):
        """
        Return a quote for a instrument
        of a given ib object


        Args:
            cex
            instrument

        Returns:
            quote
        """
        try:
            instrument = await self.replace_instrument(instrument)

            # todo add support for multiple contract type (Forex, stock, index, option)
            contract = Forex(instrument, "SMART", "USD")
            self.client.reqMktData(contract)
            quote = self.client.ticker(contract)
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

        return self.client.accountSummary(self.account)

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
            return self.client.positions()
        except Exception as e:
            logger.error("{} Error {}", self.name, e)

    async def pre_order_checks(self, order_params):
        """ """
        return True

    async def get_trading_asset_balance(self):
        """ """
        return self.client.accountSummary(self.account_number)

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
            # params = {
            #     "stopLoss": {
            #         "triggerPrice": order_params.get("stop_loss"),
            #         # "price": order_params.get("action") * 0.98,
            #     },
            #     "takeProfit": {
            #         "triggerPrice": order_params.get("take_profit"),
            #         # "price": order_params.get("action") * 0.98,
            #     },
            # }
            logger.debug("amount {}", amount)
            pre_order_checks = await self.pre_order_checks(order_params)
            logger.debug("pre_order_checks {}", pre_order_checks)

            if amount and pre_order_checks:
                # if order :=
                # todo add support for multiple contract type
                contract = Forex(instrument, "SMART", "USD")
                order = Order()
                order.action = order_params["action"]  # 'BUY' or 'SELL'
                order.orderType = order_params["order_type"] or "MKT"
                order.totalQuantity = order_params["quantity"]

                # Set limit price if it's a limit order
                # if order.orderType == 'LMT':
                #     order.lmtPrice = order_details['limitPrice']

                trade = self.client.placeOrder(contract, order)
                return await self.get_trade_confirmation(trade, instrument, action)
            return f"Error executing {self.name}"

        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return f"Error executing {self.name}"
