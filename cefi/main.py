import ccxt

from .config import settings


class CexExchange:
    """
    CEX Object to support CEX
    via CCXT library
    https://github.com/ccxt/ccxt

    Args:
        None

    Returns:
        None

    """

    def __init__(self):
        """
        Initialize the CEX object to interact with
        CEX exchange support by CCXT library

        """

        if settings.cex_name:
            client = getattr(ccxt, settings.cex_name)
            self.cex = client(
                {
                    "apiKey": settings.cex_api,
                    "secret": settings.cex_secret,
                    "password": (settings.cex_password or ""),
                    "enableRateLimit": True,
                    "options": {
                        "defaultType": settings.cex_defaulttype,
                    },
                }
            )
            if settings.cex_testmode:
                self.cex.set_sandbox_mode("enabled")
            self.commands = settings.ccxt_commands
            self.account = self.cex.uid
            self.exchange_name = self.cex.id

    async def get_info(self):
        """
        Retrieves information about the exchange
        and the account.

        :return: A formatted string containing
        the exchange name and the account information.
        :rtype: str
        """
        # account_info = self.cex.fetchAccounts().get('main')
        # method not implemented yet
        return f"💱 {self.exchange_name}\n🪪 {self.account}"

    async def get_help(self):
        """
        Get the help information for the current instance.

        Returns:
            A string containing the available commands.
        """
        return f"{self.commands}\n"

    async def get_quote(self, symbol):
        """
        return main asset balance.

        Args:
            symbol

        Returns:
            quote
        """

        return f"🏦 {self.cex.fetchTicker(symbol).get('last')}"

    async def get_trading_asset_balance(self):
        """
        return main asset balance.

        Args:
            None

        Returns:
            balance
        """
        return self.cex.fetchBalance()[f"{settings.trading_asset}"]["free"]

    async def get_account_balance(self):
        """
        return account balance.

        Args:
            None

        Returns:
            balance

        """
        raw_balance = self.cex.fetch_free_balance()
        return (
            "🏦 Balance\n"
            + "".join(
                f"{iterator}: {value} \n"
                for iterator, value in filtered_balance.items()
            )
            if (
                filtered_balance := {
                    k: v for k, v in raw_balance.items() if v is not None and v > 0
                }
            )
            else "🏦 No Balance"
        )

    async def get_account_position(self):
        """
        return account position.

        Args:
            None

        Returns:
            position

        """
        open_positions = self.cex.fetch_positions()
        open_positions = [p for p in open_positions if p["type"] == "open"]
        position = "📊 Position\n" + str(open_positions)
        position += str(
            await self.cex.fetch_balance(
                {
                    "type": "margin",
                }
            )
        )
        return position

    async def get_account_pnl(self):
        """
        return account pnl.

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
        quantity = order_params.get("quantity", settings.trading_risk_amount)

        try:
            if not action or not instrument:
                return
            if await self.get_account_balance() == "No Balance":
                return "⚠️ Check Balance"

            asset_out_quote = float(self.cex.fetchTicker(f"{instrument}").get("last"))
            asset_out_balance = await self.get_trading_asset_balance()

            if not asset_out_balance:
                return

            transaction_amount = (
                asset_out_balance * (float(quantity) / 100) / asset_out_quote
            )

            trade = self.cex.create_order(
                instrument,
                settings.cex_ordertype,
                action,
                transaction_amount,
                # price=None
            )

            if not trade:
                return

            trade_confirmation = (
                f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
            )
            trade_confirmation += f"➕ Size: {round(trade['amount'], 4)}\n"
            trade_confirmation += f"⚫️ Entry: {round(trade['price'], 4)}\n"
            trade_confirmation += f"ℹ️ {trade['id']}\n"
            trade_confirmation += f"🗓️ {trade['datetime']}"

            return trade_confirmation

        except Exception as e:
            return f"⚠️ order execution: {e}"
