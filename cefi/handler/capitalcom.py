"""

Capital.com API client


"""

import asyncio

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
        self._build_client()
        if self.client:
            self.accounts_data = self.client.all_accounts()
            logger.debug("Account data: {}", self.accounts_data)
            self.account_number = self.accounts_data["accounts"][0]["accountId"]
            logger.debug("Account number: {}", self.account_number)
            logger.debug("Session details: {}", self.client.get_sesion_details())
        else:
            logger.warning("No capital.com client. Verify settings.")

    def _build_client(self):
        """
        Builds and sets the client based on the testmode flag.

        Capital.com session last only 10 minutes

        """
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
            logger.debug("Client: {}", self.client)
            if self.client.accounts_data():
                return self.client
            else:
                logger.warning("No valid capital.com client. Verify settings.")
                self.client = None
        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            self.client = None
            return e

    async def get_quote(self, instrument):
        """
        Asynchronously fetches a ask/offer quote
        for the specified instrument.

        :param instrument: The instrument for which the quote is to be fetched.
        :return: The fetched quote.
        """
        self._build_client()
        logger.debug("Instrument: {}", instrument)
        instrument = await self.replace_instrument(instrument)
        logger.debug("Changed Instrument: {}", instrument)
        # search_markets = self.client.searching_market(searchTerm=instrument)
        await asyncio.sleep(1)  # Wait for 1 second
        # logger.debug("Instrument verification: {}", search_markets)

        market = self.client.single_market(instrument)
        # logger.debug("market: {}", market)

        quote = market["snapshot"]["offer"]
        logger.debug("Quote: {}", quote)

        return float(quote)

    # Alias for get_quote
    get_offer = get_quote

    async def get_bid(self, instrument):
        """
        Asynchronously retrieves the bid
        for the specified instrument.

        Args:
            instrument: The instrument for which
            the bid is to be retrieved.

        Returns:
            The bid for the specified instrument.
        """
        self._build_client()
        logger.debug("Instrument: {}", instrument)
        instrument = await self.replace_instrument(instrument)
        logger.debug("Changed Instrument: {}", instrument)
        # search_markets = self.client.searching_market(searchTerm=instrument)
        await asyncio.sleep(1)  # Wait for 1 second
        # logger.debug("Instrument verification: {}", search_markets)

        market = self.client.single_market(instrument)
        # logger.debug("market: {}", market)

        quote = market["snapshot"]["bid"]
        logger.debug("Quote: {}", quote)

        return float(quote)

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
        if positions := self.client.all_positions():
            extracted_positions = []
            for position_data in positions.get("positions", []):
                position_details = position_data.get("position", {})
                market_details = position_data.get("market", {})
                epic = market_details.get("epic", "")
                upl = position_details.get("upl", 0)
                extracted_positions.append(f"{epic}: {upl}")
            return "\n".join(extracted_positions)

    async def calculate_pnl(self, period=None):
        """
        no pnl info available via openapi endpoint

        Args:
            None

        Returns:
            pnl
        """
        # end_date = datetime.now()
        # formatted_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")
        # logger.debug("{} {}", start_date, formatted_end_date)
        # history = self.client.account_activity_history(
        #     fr=start_date, to=formatted_end_date, detailed=True
        # )
        # logger.debug("History: {}", history)

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

    async def get_instrument_min_amount(self, instrument):
        """
        Get the minimum amount needed for a specific instrument.

        Args:
            instrument (str): The instrument for which the minimum amount is needed.

        Returns:
            float: The minimum amount needed for the specified instrument.
        """
        instrument_info = self.client.single_market(instrument)
        logger.debug("instrument_info {}", instrument_info)
        minimum_amount = (
            instrument_info.get("dealingRules", {})
            .get("minDealSize", {})
            .get("value", 0)
        )
        logger.debug("Minimum Amount Needed {}", minimum_amount)
        return float(minimum_amount)

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
            min_amount = await self.get_instrument_min_amount(instrument)
            amount = max(amount, min_amount)
            logger.debug("Amount to execute {}", amount)
            await asyncio.sleep(1)  # Wait for 1 second

            if not (await self.pre_order_checks(order_params)):
                return f"Error executing {self.name}"

            decimals = await self.get_instrument_decimals(instrument)
            await asyncio.sleep(1)  # Wait for 1 second

            offer = await self.get_offer(instrument)
            await asyncio.sleep(1)  # Wait for 1 second

            bid = await self.get_bid(instrument)
            await asyncio.sleep(1)  # Wait for 1 second

            logger.debug("bid {}", bid)
            logger.debug("offer {}", offer)
            profit_price = (
                (offer + (int(order_params.get("take_profit", 0)) / (10**decimals)))
                if action_str == "BUY"
                else (bid - (int(order_params.get("take_profit", 0)) / (10**decimals)))
            )
            stop_price = (
                (bid - (int(order_params.get("stop_loss", 0)) / (10**decimals)))
                if action_str == "BUY"
                else (offer + (int(order_params.get("stop_loss", 0)) / (10**decimals)))
            )
            logger.debug("stop price {}", stop_price)
            logger.debug("profit price {}", profit_price)
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

            if "errorCode" in order:
                logger.error(f"Error placing order: {order['errorCode']}")
                return str(order["errorCode"])

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

    async def modify_position(self, order_params):
        """
        Modify parameters such as SL / TP of a position that is opened
        No capability to modify amount to reduce

        Args:
            order_params (dict):
                action(str)
                instrument(str)
                quantity(int)
                stop_price(int)
                stop_distance(int)
                stop_amount(int)
                take_profit_price(int)
                take_profit_distance(int)
                take_profit_amount(int)

        Returns:
            trade_confirmation(dict)

        """
        try:
            order = self.client.update_the_position(
                dealid=order_params["id"],
                gsl=order_params.get("trailing_stop_enabled", False),
                tsl=order_params.get("trailing_stop_enabled", False),
                stop_level=order_params.get("stop_price"),
                stop_distance=order_params.get("stop_distance"),
                stop_amount=order_params.get("stop_amount"),
                profit_level=order_params.get("take_profit_price"),
                profit_distance=order_params.get("take_profit_distance"),
                profit_amount=order_params.get("take_profit_amount"),
            )

            if "errorCode" in order:
                logger.error(f"Error modifying order: {order['errorCode']}")
                return str(order["errorCode"])

            logger.debug("Order: {}", order)
            deal_reference = order["dealReference"]
            order_check = self.client.position_order_confirmation(
                deal_reference=deal_reference
            )

            trade = {
                "amount": order_check.get("size", 0),
                "price": order_check.get("level", 0),
                "id": order_check.get("dealId", ""),
                "datetime": order_check.get("date", ""),
            }
            return await self.get_trade_confirmation(
                trade, order_params.get("instrument"), order_params.get("action")
            )
        except Exception as e:
            logger.error("{} Error {}", self.name, e)
            return f"Error executing {self.name}: {e}"
