import ccxt
from loguru import logger

from .config import settings


class CexTrader:
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

    def __init__(self):
        """
        Initialize the CexTrader object

        """

        self.commands = settings.ccxt_commands
        exchanges = settings.cex
        self.cex_info = []
        try:
            for exchange in exchanges:
                logger.debug(f"Loading {exchange}")
                client = getattr(ccxt, exchanges[exchange]["cex_name"])
                cx_client = client(
                    {
                        "apiKey": exchanges[exchange]["cex_api"],
                        "secret": exchanges[exchange]["cex_secret"],
                        "password": (exchanges[exchange]["cex_password"]),
                        "enableRateLimit": True,
                        "options": {
                            "defaultType": exchanges[exchange]["cex_defaulttype"],
                        },
                    }
                )
                if exchanges[exchange]["cex_testmode"]:
                    cx_client.set_sandbox_mode("enabled")
                account = cx_client.uid
                exchange_name = cx_client.id
                trading_asset = exchanges[exchange]["trading_asset"]
                separator = exchanges[exchange]["trading_asset_separator"]
                trading_risk_amount = exchanges[exchange]["trading_risk_amount"]
                exchange_defaulttype = exchanges[exchange]["cex_defaulttype"]
                exchange_ordertype = exchanges[exchange]["cex_ordertype"]
                self.cex_info.append(
                    {
                        "cex": cx_client,
                        "account": account,
                        "exchange_name": exchange_name,
                        "exchange_defaulttype": exchange_defaulttype,
                        "exchange_ordertype": exchange_ordertype,
                        "trading_asset": trading_asset,
                        "separator": separator,
                        "trading_risk_amount": trading_risk_amount,
                    }
                )
        except Exception as e:
            logger.error(e)

    async def get_help(self):
        """
        Get the help information for the current instance.

        Returns:
            A string containing the available commands.
        """
        return f"{self.commands}\n"

    async def get_info(self):
        """
        Retrieves information about the exchange
        and the account.

        :return: A formatted string containing
        the exchange name and the account information.
        :rtype: str
        """

        info = ""
        for item in self.cex_info:
            exchange_name = item["exchange_name"]
            account = item["account"]
            info += f"💱 {exchange_name}\n🪪 {account}\n\n"
        return info.strip()

    async def get_quotes(self, symbol):
        """
        Return a list of quotes.

        Args:
            symbol

        Returns:
            quotes
        """

        quotes = []
        for item in self.cex_info:
            cex = item["cex"]
            instrument = (symbol + item["separator"] + item["trading_asset"])
            exchange_name = item["exchange_name"]
            quote = await self.get_quote(cex, instrument)
            logger.debug("Quote {}", quote)
            quotes.append(f"🏦 {exchange_name}: {quote}")
        return "\n".join(quotes)

    async def get_quote(self, cx_client, symbol):
        """
        Return a quote for a symbol
        of a given exchange ccxt object


        Args:
            cex
            symbol

        Returns:
            quote
        """
        try:
            ticker = cx_client.fetch_ticker(symbol)
            logger.debug("ticker: {}", ticker)
            return ticker["last"]
        except Exception as e:
            logger.error("get_quote: {}", e)
            return "No Quote"

    async def get_account_balances(self):
        """
        Return account balance.

        Args:
            None

        Returns:
            balance

        """
        balance_info = []
        for item in self.cex_info:
            cex = item["cex"]
            exchange_name = item["exchange_name"]
            balance = await self.get_account_balance(cex)
            balance_info.append(f"🏦 Balance for {exchange_name}:\n{balance}")
        return "\n".join(balance_info)

    async def get_account_balance(self, cx_client):
        """
        return account balance of
        a given ccxt exchange

        Args:
            None

        Returns:
            balance

        """
        try:
            raw_balance = cx_client.fetch_free_balance()
            if filtered_balance := {
                k: v for k, v in raw_balance.items() if v is not None and v > 0
            }:
                balance_str = "".join(
                    f"{iterator}: {value} \n"
                    for iterator, value in filtered_balance.items()
                )
                return f"{balance_str}"
        except Exception as e:
            logger.error(e)
            return "No Balance"

    async def get_account_positions(self):
        """
        return account position.

        Args:
            None

        Returns:
            position

        """

        position_info = []
        for item in self.cex_info:
            cex = item["cex"]
            exchange_name = item["exchange_name"]
            positions = await self.get_account_position(cex)
            position_info.append(f"📊 Position for {exchange_name}:\n{positions}")
        return "\n".join(position_info)

    async def get_account_position(self, cx_client):
        """
        Return account position.
        of a given exchange

        Args:
            None

        Returns:
            position

        """
        try:
            positions = cx_client.fetch_positions()
            if positions := [p for p in positions if p["type"] == "open"]:
                return f"{positions}"
        except Exception as e:
            logger.error(e)
            return "No Position"

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
        action = order_params.get("action")
        instrument = order_params.get("instrument")
        confirmation_info = []
        if not action or not instrument:
            return

        for item in self.cex_info:
            cex = item["cex"]
            exchange_name = item["exchange_name"]
            order_type = item["exchange_ordertype"]
            trading_asset = item["trading_asset"]
            logger.debug("trading_asset {}", trading_asset)
            instrument = (instrument + item["separator"] + item["trading_asset"])
            try:
                if await self.get_account_balance(cex) == "No Balance":
                    logger.warning("⚠️ Check Balance")
                    confirmation_info.append(f"{exchange_name}:\nNo Funding")
                    continue
                asset_out_quote = await self.get_quote(cex, instrument)
                logger.debug("asset_out_quote {}", asset_out_quote)
                if asset_out_quote == "No Quote":
                    confirmation_info.append(f"{exchange_name}:\nNo quote")
                    continue
                asset_out_balance = cex.fetchBalance()[f"{trading_asset}"]["free"]
                logger.debug("asset_out_balance {}", asset_out_balance)
                if not asset_out_balance:
                    confirmation_info.append(f"{exchange_name}:\nNo Funding")
                    continue

                quantity = order_params.get("quantity", item["trading_risk_amount"])
                transaction_amount = (
                    asset_out_balance * (float(quantity) / 100) / asset_out_quote
                )

                trade = cex.create_order(
                    instrument,
                    order_type,
                    action,
                    transaction_amount,
                    # price=None
                )

                if not trade:
                    confirmation_info.append(f"{exchange_name}:\nNo Execution")
                    continue

                trade_confirmation = (
                    f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
                )
                trade_confirmation += f"⚫ {round(trade['amount'], 4)}\n"
                trade_confirmation += f"🔵 {round(trade['price'], 4)}\n"
                trade_confirmation += f"🟢 {round(trade['price'], 4)}\n"
                trade_confirmation += f"🔴 {round(trade['price'], 4)}\n"
                trade_confirmation += f"ℹ️ {trade['id']}\n"
                trade_confirmation += f"🗓️ {trade['datetime']}"
                if trade_confirmation:
                    confirmation_info.append(f"{exchange_name}:\n{trade_confirmation}")
                else:
                    confirmation_info.append(f"Error executing {exchange_name}")

            except Exception as e:
                logger.debug("{} Error {}", exchange_name, e)
                confirmation_info.append(f"{exchange_name}: Error {e}")
                continue

        return confirmation_info
