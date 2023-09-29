import ccxt
from loguru import logger

from .config import settings
from .protocol.ccxt import CexCcxt


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
                client = self._create_client(
                    protocol="ccxt",
                    name=exchanges[exchange]["name"],
                    api_key=exchanges[exchange]["api_key"],
                    secret=exchanges[exchange]["secret"],
                    password=exchanges[exchange]["password"],
                    testmode=exchanges[exchange]["testmode"],
                    defaulttype=exchanges[exchange]["defaulttype"],
                    ordertype=exchanges[exchange]["ordertype"],
                    trading_risk_amount=exchanges[exchange]["trading_risk_amount"],
                    trading_asset=exchanges[exchange]["trading_asset"],
                    trading_asset_separator=exchanges[exchange][
                        "trading_asset_separator"
                    ],
                    mapping=exchanges[exchange]["mapping"],
                )
                self.cex_info.append(client)
                logger.debug(f"Loaded {exchange}")

        except Exception as e:
            logger.error("CexTrader init: {}", e)

    def _create_client(self, **kwargs):
        """
        Get the handler object based on the specified platform.

        Returns:
            object: The handler object.
        """
        protocol = kwargs["protocol"]
        logger.debug("get handler {}", protocol)
        if protocol == "ccxt":
            logger.debug("get ccxt client")
            return CexCcxt(**kwargs)
        else:
            logger.error("Invalid platform specified {}", protocol)

    async def get_info(self):
        """
        Retrieves information about the exchange
        and the account.

        :return: A formatted string containing
        the exchange name and the account information.
        :rtype: str
        """

        info = "".join(f"💱 {cex.name}\n🪪 {cex.account}\n\n" for cex in self.cex_info)
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
        for cex in self.cex_info:
            quote = await cex.get_quote(symbol)
            quotes.append(f"🏦 {cex.name}: {quote}")
        return "\n".join(quotes)

    async def get_balances(self):
        """
        Return account balance.

        Args:
            None

        Returns:
            balance

        """
        balance_info = []
        for cex in self.cex_info:
            balance = await cex.get_account_balance()
            balance_info.append(f"🏦 Balance for {cex.name}:\n{balance}")
        return "\n".join(balance_info)

    async def get_positions(self):
        """
        return account position.

        Args:
            None

        Returns:
            position

        """

        position_info = []
        for _ in self.cex_info:
            positions = await _.get_account_position()
            position_info.append(f"📊 Position for {_.name}:\n{positions}")
        return "\n".join(position_info)

    async def get_pnls(self):
        """
        Return account pnl.

        Args:
            None

        Returns:
            pnl
        """

        pnl_info = []
        for cex in self.cex_info:
            pnls = await cex.get_account_pnl()
            pnl_info.append(f"📊 PnL for {cex.name}:\n{pnls}")
            return "\n".join(pnl_info)

    async def submit_order(self, order_params):
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
        order = []
        # if not action or not instrument:
        #     return

        for cex in self.cex_info:
            try:
                trade = await cex.execute_order(order_params)
                order.append(trade)

            except Exception as e:
                logger.debug("{} Error {}", cex.name, e)
                continue

        return order
