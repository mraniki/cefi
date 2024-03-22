"""

Capital.com API client


"""

from capitalcom.client import Client
from loguru import logger

from .client import CexClient


class CexCapital(CexClient):
    """
    Capital.com client
    using
    https://pypi.org/project/capitalcom-python/
    via Capital.com API endpoint
    https://open-api.capital.com/
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
        Initialize the capital.com client

        """
        super().__init__(**kwargs)
        self.client = Client(
            log=self.user_id,
            password=self.password,
            api_key=self.api_key,
        )

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

            ticker = self.client.single_market(instrument)
            quote = ticker["snapshot"]["offer"]
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
        accounts_data = self.client.all_accounts()
        accounts = accounts_data.get("accounts", [])

        balances = [
            f"{account['accountName']}: {account['balance']['balance']}\n"
            for account in accounts
            if "balance" in account and account["balance"].get("balance") is not None
        ]

        return "".join(balances)

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
            if positions := self.client.all_positions():
                return f"{positions}"
        except Exception as e:
            logger.error("{} Error {}", self.name, e)

    async def pre_order_checks(self, order_params):
        """ """
        return True

    async def get_trading_asset_balance(self):
        """
        Return the available balance of the trading asset from the account.

        Returns:
            float: The available balance of the trading asset.
        """
        accounts_data = self.client.all_accounts()
        return next(
            (
                account["balance"]["available"]
                for account in accounts_data["accounts"]
                if account["accountName"] == self.trading_asset
            ),
            0,
        )

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
                if order := self.client.place_the_position(
                    direction=action,
                    epic=instrument,
                    size=amount,
                ):
                    return await self.get_trade_confirmation(order, instrument, action)
            return f"Error executing {self.name}"

        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return f"Error executing {self.name}"
