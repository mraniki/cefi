"""
Interactive Brokers client using ibind library
and ibeam docker gateway
"""

import asyncio

from ibind import IbkrClient, QuestionType, StockQuery, make_order_request
from loguru import logger

from ._client import CexClient


class IbHandler(CexClient):
    """
    CEX client for IBKR using ibind library

    Args:
        None

    Returns:
        None
    """

    def __init__(self, **kwargs):
        """
        Initializes the IBKR client using ibind
        """
        super().__init__(**kwargs)
        self.client = None
        self.account_number = None
        if not self.host:
            self.host = "http://ibeam:5000/v1/api/"

        if not self.enabled:
            return

        try:
            # Initialize IbkrClient with IBeam gateway
            # or your own gateway URL
            # for ibeam you can use the preconfigured
            # docker https://github.com/Voyz/ibeam
            self.client = IbkrClient(url=self.host)

            # Verify connection
            tickle_result = self.client.tickle()
            if (
                not tickle_result.data.get("iserver", {})
                .get("authStatus", {})
                .get("authenticated", False)
            ):
                raise ConnectionError("Failed to authenticate with IBKR")

            # Get account number
            accounts = self.client.portfolio_accounts().data
            if not accounts:
                raise ValueError("No trading accounts found")
            self.account_number = accounts[0]["accountId"]

            logger.debug("Connected to IBKR successfully")
            logger.debug(f"Account number: {self.account_number}")

        except Exception as e:
            logger.error(f"IbkrClient initialization error: {e}")
            raise

    async def _async_request(self, fn, *args, **kwargs):
        """Helper to run synchronous ibind calls in thread pool"""
        return await asyncio.to_thread(fn, *args, **kwargs)

    async def get_info(self):
        """
        Retrieves account information
        """
        result = await self._async_request(
            self.client.portfolio_account_summary, self.account_number
        )
        return result.data

    async def get_quote(self, instrument):
        """
        Get market data snapshot for instrument
        """
        try:
            instrument = await self.replace_instrument(instrument)
            conid = await self.search_contract(instrument)

            if not conid:
                logger.warning(f"No contract found for {instrument}")
                return None

            # Get real-time market data (adjust fields as needed)
            result = await self._async_request(
                self.client.marketdata_snapshot,
                conid,
                fields=["31", "84", "86"],  # bid, ask, last price
            )
            return result.data

        except Exception as e:
            logger.error(f"Error getting quote: {e}")
            return None

    async def get_account_balance(self):
        """
        Get account balance summary
        """
        result = await self._async_request(
            self.client.portfolio_account_summary, self.account_number
        )
        return result.data

    async def get_account_position(self):
        """
        Get current positions
        """
        result = await self._async_request(
            self.client.portfolio_positions, self.account_number
        )
        return result.data

    async def search_contract(self, instrument):
        """
        Find contract CONID using symbol and mapping configuration
        """
        try:
            # Find instrument in mapping
            asset = next(
                (
                    item
                    for item in self.mapping
                    if item["id"] == instrument or item["alt"] == instrument
                ),
                None,
            )

            if not asset:
                logger.warning(f"Instrument {instrument} not found in mapping")
                return None

            # Build stock query from mapping
            query = StockQuery(
                symbol=asset["id"],
                contract_conditions={
                    "exchange": asset.get("exchange", "SMART"),
                    "currency": asset.get("currency", "USD"),
                    "secType": asset.get("type", "STK"),
                },
            )

            # Get CONID
            result = await self._async_request(
                self.client.stock_conid_by_symbol, query, default_filtering=True
            )

            return result.data.get(instrument)

        except Exception as e:
            logger.error(f"Contract search error: {e}")
            return None

    async def execute_order(self, order_params):
        """
        Execute order using IBKR REST API
        """
        try:
            instrument = await self.replace_instrument(order_params["instrument"])
            conid = await self.search_contract(instrument)

            if not conid:
                return {"error": f"Contract not found for {instrument}"}

            # Create order request
            order_request = make_order_request(
                conid=conid,
                side=order_params["action"].upper(),
                quantity=order_params.get("quantity", 1),
                order_type=order_params.get("order_type", "MKT"),
                acct_id=self.account_number,
                price=order_params.get("price"),
                coid=order_params.get("client_order_id"),
            )

            # Define standard answers for order questions
            answers = {
                QuestionType.PRICE_PERCENTAGE_CONSTRAINT: True,
                QuestionType.ORDER_VALUE_LIMIT: True,
                "_DEFAULT": True,  # Accept any unexpected questions
            }

            # Place order
            result = await self._async_request(
                self.client.place_order, order_request, answers=answers
            )

            if result.data.get("order_id"):
                return {
                    "status": "success",
                    "order_id": result.data["order_id"],
                    "details": result.data,
                }
            return {"status": "error", "message": result.data}

        except Exception as e:
            logger.error(f"Order execution error: {e}")
            return {"error": str(e)}

    async def get_trading_asset_balance(self):
        """Alias for get_account_balance"""
        return await self.get_account_balance()

    async def pre_order_checks(self, order_params):
        """Implement custom pre-trade checks if needed"""
        return True
