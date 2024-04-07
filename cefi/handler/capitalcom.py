"""

Capital.com API client


"""

from datetime import datetime, timedelta

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

    Methods:
        get_quote(self, instrument)
        get_account_balance(self)
        get_account_position(self)
        pre_order_checks(self, order_params)
        get_trading_asset_balance(self)
        get_instrument_decimals(self, instrument)
        execute_order(self, order_params)


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

    async def get_bid(self, instrument):
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

            quote = market["snapshot"]["bid"]
            logger.debug("Quote: {}", quote)

            return quote
        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return e

    # Alias for get_quote
    get_offer = get_quote

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
                extracted_positions = []
                for position_data in positions.get("positions", []):
                    position_details = position_data.get("position", {})
                    market_details = position_data.get("market", {})
                    epic = market_details.get("epic", "")
                    upl = position_details.get("upl", 0)
                    extracted_positions.append(f"{epic}: {upl}")
                return "\n".join(extracted_positions)
        except Exception as e:
            logger.error(f"{self.name} Error {e}")

    async def get_account_pnl(self, period=None):
        """
        Return account pnl.

        Args:
            None

        Returns:
            pnl
        """
        today = datetime.now().date()
        if period is None:
            start_date = today
        elif period == "W":
            start_date = today - timedelta(days=today.weekday())
        elif period == "M":
            start_date = today.replace(day=1)
        elif period == "Y":
            start_date = today.replace(month=1, day=1)

        end_date = datetime.now()
        formatted_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")
        logger.debug("{} {}", start_date, formatted_end_date)
        # history = self.client.account_activity_history(
        #     fr=start_date, to=formatted_end_date, detailed=True, type="TRADE"
        # )
        # no pnl info available via openapi endpoint
        return 0

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

    async def get_instrument_decimals(self, instrument):
        """
        Get the number of decimal places for the instrument.

        Returns:
            int: The number of decimal places for the instrument.
        """
        instrument_info = self.client.single_market(instrument)
        decimals = instrument_info.get("snapshot", {}).get("decimalPlacesFactor", 0)
        logger.debug("Decimals {}", decimals)
        return int(decimals)

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

            decimals = await self.get_instrument_decimals(instrument)

            profit_price = (
                (
                    await self.get_offer(instrument)
                    + (order_params.get("take_profit", 0) / (10**decimals))
                )
                if action_str == "BUY"
                else (
                    await self.get_bid(instrument)
                    - (order_params.get("take_profit", 0) / (10**decimals))
                )
            )
            stop_price = (
                (
                    await self.get_bid(instrument)
                    - (order_params.get("stop_loss", 0) / (10**decimals))
                )
                if action_str == "BUY"
                else (
                    self.get_offer(instrument)
                    + (order_params.get("stop_loss", 0) / (10**decimals))
                )
            )
            logger.debug("stop price {}", stop_price)
            logger.debug("profit price {}", profit_price)
            try:
                order = self.client.place_the_position(
                    direction=action,
                    epic=instrument,
                    size=amount,
                    gsl=False,
                    tsl=False,
                    stop_level=stop_price,
                    stop_distance=None,
                    stop_amount=None,
                    profit_level=profit_price,
                    profit_distance=None,
                    profit_amount=None,
                )
                # Check if the order response contains an errorCode
                if "errorCode" in order:
                    # Handle the error, e.g., log it or return a specific message
                    logger.error(f"Error placing order: {order['errorCode']}")
                    return f"Error placing order: {order['errorCode']}"
            except Exception as e:
                return str(e)

            logger.debug("Order: {}", order)
            deal_reference = order["dealReference"]
            order_check = self.client.position_order_confirmation(
                deal_reference=deal_reference
            )

            trade = {
                "amount": order_check.get("size", 0),
                "price": order_check.get("level", 0),
                "takeProfitPrice": profit_price,
                "stopLossPrice": stop_price,
                "id": order_check.get("dealId", ""),
                "datetime": order_check.get("date", ""),
            }
            return await self.get_trade_confirmation(trade, instrument, action)

        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return f"Error executing {self.name}: {e}"
