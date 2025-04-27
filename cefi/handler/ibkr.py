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

    Requires ibind library: pip install ibind
    Requires IBeam gateway running: https://github.com/Voyz/ibeam

    Configuration in settings.toml:
    [cex.ibkr]
    enabled = true
    host = "http://127.0.0.1:5000" # IBeam URL
    account = "YOUR_IBKR_ACCOUNT_UXXXXXXX"
    mapping = [
        {
            id = "EURUSD",
            alt = "EUR.USD",
            secType = "CASH",
            exchange = "IDEALPRO",
            currency = "USD",
        },
        {
            id = "SPY",
            alt = "SPY",
            secType = "STK",
            exchange = "SMART",
            currency = "USD",
        },
        # Add other mappings here...
    ]
    """

    def __init__(self, **kwargs):
        """
        Initializes the IBKR handler using ibind.
        Loads configuration from kwargs.
        """
        super().__init__(**kwargs)
        # Load config from kwargs provided by CexClient
        self.client = None
        self.enabled = kwargs.get('enabled', False)
        self.host = kwargs.get('host', "http://127.0.0.1:5000") # Default IBeam host
        self.account_number = kwargs.get('account')
        self.mapping = kwargs.get('mapping', []) # Load mapping from config

        if not self.enabled:
            logger.info("IBKR handler is disabled.")
            return

        if not self.account_number:
            logger.warning(
                "IBKR account number not found in configuration. "
                "Some features might not work."
            )
            # Optionally raise error if account number is strictly required
            # raise ValueError("IBKR account number is required in configuration.")

        if not self.mapping:
            logger.warning("IBKR mapping is empty or not found in configuration.")


        try:
            logger.debug(f"Attempting to connect IBKR client to {self.host}")
            # Initialize IbkrClient with IBeam gateway URL from config
            self.client = IbkrClient(url=self.host)

            # Verify connection
            tickle_result = self.client.tickle()
            iserver_status = tickle_result.data.get("iserver", {})
            auth_status = iserver_status.get("authStatus", {})
            is_authenticated = auth_status.get("authenticated", False)

            if not is_authenticated:
                logger.error(
                    f"Failed to authenticate with IBKR via {self.host}. "
                    f"Check IBeam status and connection."
                )
                raise ConnectionError("Failed to authenticate with IBKR")

            logger.debug(f"IBKR Tickle Result: {tickle_result.data}")

            # If account number wasn't provided, try to fetch it (optional)
            if not self.account_number:
                accounts = self.client.portfolio_accounts().data
                if (
                    accounts
                    and isinstance(accounts, list)
                    and "accountId" in accounts[0]
                ):
                    self.account_number = accounts[0]["accountId"]
                    logger.info(f"Fetched IBKR Account ID: {self.account_number}")
                else:
                    logger.error("Could not fetch IBKR account number automatically.")
                    # Decide whether to raise error or proceed without account number
                    raise ValueError("Failed to fetch IBKR account number.")

            logger.success(
                f"Connected to IBKR successfully. Account: {self.account_number}"
            )

        except ConnectionError as ce:
             logger.error(f"IBKR ConnectionError: {ce}")
             self.enabled = False # Disable handler if connection fails
             # Optionally re-raise or handle connection failure
             # raise ce
        except Exception as e:
            logger.error(f"IbkrClient initialization error: {e}")
            self.enabled = False # Disable handler on other errors
            # Optionally re-raise
            # raise

    async def _async_request(self, fn, *args, **kwargs):
        """Helper to run synchronous ibind calls in thread pool"""
        if not self.enabled or not self.client:
            logger.warning("IBKR client not initialized or disabled.")
            return None # Or raise appropriate exception
        try:
            return await asyncio.to_thread(fn, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing IBKR async request {fn.__name__}: {e}")
            return None # Or re-raise specific exceptions

    async def get_info(self):
        """
        Retrieves account information (Summary)
        """
        if not self.account_number:
            return {"error": "IBKR account number not configured."}
        result = await self._async_request(
            self.client.portfolio_account_summary, self.account_number
        )
        return result.data if result else None

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
        if not self.account_number:
            return {"error": "IBKR account number not configured."}
        result = await self._async_request(
            self.client.portfolio_positions, self.account_number
        )
        return result.data if result else None

    async def search_contract(self, instrument):
        """
        Find contract CONID using symbol and mapping configuration.
        Uses secType, exchange, currency from the mapping.
        """
        if not self.client:
            return None # Client not initialized
        if not self.mapping:
            return None # No mapping configured

        try:
            # Find instrument in mapping based on id or alt
            asset = next(
                (
                    item
                    for item in self.mapping
                    if isinstance(item, dict)
                    and (
                        item.get("id") == instrument
                        or item.get("alt") == instrument
                    )
                ),
                None,
            )

            if not asset:
                logger.warning(f"Instrument '{instrument}' not found in IBKR mapping.")
                return None

            # Get required details from mapping
            # Prefer 'alt' if exists, else 'id'
            symbol = asset.get("alt", asset.get("id"))
            secType = asset.get("secType")
            # Default to SMART if not specified
            exchange = asset.get("exchange", "SMART")
            # Default to USD if not specified
            currency = asset.get("currency", "USD")

            if not symbol or not secType:
                logger.error(
                    f"Incomplete mapping for {instrument}: Missing 'id'/'alt' or "
                    f"'secType'. Mapping: {asset}"
                )
                return None

            logger.debug(
                f"Searching IBKR contract for: Symbol={symbol}, SecType={secType}, "
                f"Exchange={exchange}, Currency={currency}"
            )

            # TODO: ibind might require different query types/functions for non-STK
            # secTypes. Using StockQuery for now, may need adjustment based on
            # ibind capabilities. Example: Might need FutureQuery(symbol=...,
            # exchange=..., currency=..., ...) etc.
            query = StockQuery(
                symbol=symbol,
                contract_conditions={
                    "secType": secType,
                    "exchange": exchange,
                    "currency": currency,
                    # Add other potential conditions from mapping if needed by ibind
                    # e.g., "localSymbol": asset.get("localSymbol")
                },
            )

            # Get CONID using the specific details from mapping
            # Note: default_filtering=True might be important
            result = await self._async_request(
                self.client.stock_conid_by_symbol, query, default_filtering=True
            )

            if not result or not result.data:
                 logger.warning(
                     f"IBKR contract search returned no data for query: {query}. "
                     f"Result: {result}"
                 )
                 return None

            # ibind returns a dictionary {symbol: conid} or similar
            # Extract the conid associated with the searched symbol
            conid = result.data.get(symbol)

            if not conid:
                logger.warning(
                    f"Could not extract CONID for symbol '{symbol}' from IBKR result: "
                    f"{result.data}"
                )
                return None

            logger.debug(f"Found CONID {conid} for instrument {instrument} ({symbol})")
            return conid # Return the found CONID

        except Exception as e:
            logger.error(f"IBKR Contract search error for '{instrument}': {e}")
            return None

    async def execute_order(self, order_params):
        """
        Execute order using IBKR REST API
        """
        if not self.account_number:
            return {"error": "IBKR account number not configured."}
        if not self.client:
            return {"error": "IBKR client not initialized."}

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
