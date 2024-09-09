"""

Degiro client


"""

from datetime import date

from degiro_connector.trading.api import API as TradingAPI
from degiro_connector.trading.models.account import Format, ReportRequest
from degiro_connector.trading.models.credentials import build_credentials
from degiro_connector.trading.models.order import Action, Order, OrderType, TimeType
from loguru import logger

from ._client import CexClient


class DegiroHandler(CexClient):
    """
    CEX client
    via Degiro API
    https://github.com/Chavithra/degiro-connector

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
        if self.name is None:
            return
        credentials = build_credentials(
            # location="config/config.json",
            override={
                "username": self.user_id,
                "password": self.password,
                "int_account": self.broker_account_number,  # From `get_client_details`
                "totp_secret_key": self.secret,  # For 2FA
            },
        )
        client = TradingAPI(credentials=credentials)
        client.connect()
        self.accounts_data = client.get_account_info()

    async def get_quote(self, instrument):
        """
        Asynchronously fetches a ask/offer quote
        for the specified instrument.

        :param instrument: The instrument for which the quote is to be fetched.
        :return: The fetched quote.
        """
        # TODO
        # try:
        #     instrument = await self.replace_instrument(instrument)

        #     ticker = self.client.
        #     quote =
        #     logger.debug("Quote: {}", quote)
        #     return quote
        # except Exception as e:
        #     logger.error("{} Error {}", self.name, e)

    async def get_account_balance(self):
        """
        return account balance

        Args:
            None

        Returns:
            balance

        """
        return self.client.get_account_report(
            report_request=ReportRequest(
                country="FR",
                lang="fr",
                format=Format.CSV,
                from_date=date(year=date.today().year - 1, month=1, day=1),
                to_date=date.today(),
            ),
            raw=False,
        )

    async def get_account_position(self):
        """
        Return account position.

        Args:
            None

        Returns:
            position

        """
        return self.client.get_position_report(
            report_request=ReportRequest(
                country="FR",
                lang="fr",
                format=Format.XLS,
                from_date=date(year=date.today().year - 1, month=1, day=1),
                to_date=date.today(),
            ),
            raw=False,
        )

    async def pre_order_checks(self, order_params):
        """ """
        return True

    async def get_trading_asset_balance(self):
        """ """
        # TODO
        # return self.client.fetchBalance()[f"{self.trading_asset}"]["free"]

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
        # TODO: Test and fix order call
        try:
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
            order = Order(
                buy_sell=Action.BUY if action == "BUY" else Action.SELL,
                order_type=OrderType.LIMIT,
                price=12.1,
                product_id=72160,
                size=amount,
                time_type=TimeType.GOOD_TILL_DAY,
            )
            if checking_response := self.client.check_order(order=order):
                if confirmation_response := self.client.confirm_order(
                    confirmation_id=checking_response.confirmation_id,
                    order=order,
                ):
                    logger.debug("Confirmation: {}", confirmation_response)
                    return await self.get_trade_confirmation(order, instrument, action)
        except Exception as e:
            logger.error(f"{self.name} Error {e}")
            return f"Error executing {self.name}"
