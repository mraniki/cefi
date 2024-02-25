"""

Interactive Brokers client


"""

from ib_insync import IB, IBC, Contract, Order
from loguru import logger

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

        For IBC gateway setup,
        refer to https://github.com/IbcAlpha/IBC/blob/master/userguide.md

        """
        try:
            super().__init__(**kwargs)
            self.protocol = "ib"
            if self.broker_gateway:
                ibc = IBC(
                    976,
                    gateway=True,
                    tradingMode="paper" if self.testmode else "live",
                    userid=self.user_id,
                    password=self.password,
                )
                ibc.start()
                IB.run()
            self.client = IB()
            self.client.connect(
                host=self.host,
                port=self.port,
                clientId=self.broker_client_id or 1,
                readonly=False,
                account=self.broker_account_number or "",
            )
            self.name = self.client.id
            self.account_number = self.client.managedAccounts()[0]
            logger.debug("Connected to IBKR {}", self.client.isConnected())
            logger.debug("Broker_IBKR initialized with account: {}", self.account)

        except Exception as e:
            logger.error("IBC Initialization Error {}", e)
            return None

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

            if contract := self.search_contract(instrument):
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

            logger.debug("amount {}", amount)
            pre_order_checks = await self.pre_order_checks(order_params)
            logger.debug("pre_order_checks {}", pre_order_checks)

            if amount and pre_order_checks:
                if contract := self.search_contract(instrument):
                    order = Order()
                    order.action = order_params["action"]
                    order.orderType = order_params["order_type"] or "MKT"
                    order.totalQuantity = amount
                    trade = self.client.placeOrder(contract, order)
                    return await self.get_trade_confirmation(trade, instrument, action)

            return f"Error executing {self.name}"

        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return f"Error executing {self.name}"

    async def search_contract(self, instrument):
        """
        Asynchronously searches for a contract based on the given instrument.

        Args:
            self: The object instance.
            instrument: The instrument to search for.

        Returns:
            Contract: The contract matching the instrument, or None if not found.
        """
        try:
            if asset := next(
                (
                    item
                    for item in self.mapping
                    if item["id"] == instrument or item["alt"] == instrument
                ),
                None,
            ):
                return Contract(
                    secType=asset["type"],
                    symbol=asset["id"],
                    lastTradeDateOrContractMonth=asset["lastTradeDateOrContractMonth"],
                    strike=asset["strike"],
                    right=asset["right"],
                    multiplier=asset["multiplier"],
                    exchange=asset["exchange"],
                    currency=asset["currency"],
                )
            logger.warning("Asset {} not found in mapping", instrument)
            return None

        except Exception as e:
            logger.error("search_contract {} Error {}", instrument, e)
