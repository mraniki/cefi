"""

Capital.com API client


"""

from capitalcom.client import Client, DirectionType
from capitalcom.client_demo import Client as DemoClient
from loguru import logger

from .client import CexClient


class CapitalHandler(CexClient):
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
        try:
            if self.testmode:
                self.client = DemoClient(
                    log=self.user_id,
                    pas=self.password,
                    api_key=self.api_key,
                )
            else:
                self.client = Client(
                    log=self.user_id,
                    pas=self.password,
                    api_key=self.api_key,
                )
            self.accounts_data = self.client.all_accounts()
            logger.debug("Account data: {}", self.accounts_data)
            self.account_number = self.accounts_data["accounts"][0]["accountId"]
            logger.debug("Account number: {}", self.account_number)

        except Exception as e:
            logger.error("{} Error {}", self.name, e)

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
            logger.debug("Instrument: {}", instrument)
            instrument = await self.replace_instrument(instrument)
            logger.debug("Changed Instrument: {}", instrument)
            search_markets = self.client.searching_market(searchTerm=instrument)
            logger.debug("Instrument verification: {}", search_markets)

            market = self.client.single_market(instrument)
            logger.debug("Raw Quote: {}", market)

            quote = market["snapshot"]["offer"]
            logger.debug("Quote: {}", quote)

            return quote
        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return e

    async def get_account_balance(self):
        """
        return account balance of
        a given ccxt exchange

        Args:
            None

        Returns:
            balance

        """

        accounts = self.accounts_data.get("accounts", [])

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
        return next(
            (
                account["balance"]["available"]
                for account in self.accounts_data["accounts"]
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
            action_str = order_params.get("action")
            action = DirectionType[action_str]
            instrument = await self.replace_instrument(order_params.get("instrument"))
            quantity = order_params.get("quantity", self.trading_risk_amount)
            amount = await self.get_order_amount(
                quantity=quantity,
                instrument=instrument,
                is_percentage=self.trading_risk_percentage,
            )
            if not (await self.pre_order_checks(order_params)):
                return f"Error executing {self.name}"

            order = self.client.place_the_position(
                direction=action, epic=instrument, size=amount
            )
            deal_reference = order["dealReference"]
            order_check = self.client.position_order_confirmation(
                deal_reference=deal_reference
            )

            trade = {
                "amount": order_check.get("size", 0),
                "price": order_check.get("level", 0),
                "takeProfitPrice": 0,
                "stopLossPrice": 0,
                "id": order_check.get("dealId", ""),
                "datetime": order_check.get("date", ""),
            }
            return await self.get_trade_confirmation(trade, instrument, action)

        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return f"Error executing {self.name}: {e}"
