import ccxt
from loguru import logger

from cefi import __version__

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

        try:
            config = settings.cex
            self.clients = []
            for item in config:
                _config = config[item]
                if item not in ["", "template"]:
                    client = self._create_client(
                        protocol=_config.get("protocol"),
                        name=_config.get("name"),
                        api_key=_config.get("api_key"),
                        secret=_config.get("secret"),
                        password=_config.get("password"),
                        testmode=_config.get("testmode"),
                        defaulttype=_config.get("defaulttype") or "spot",
                        ordertype=_config.get("ordertype") or "market",
                        leverage_type=_config.get("leverage_type") or "isolated",
                        leverage=_config.get("leverage") or 1,
                        trading_risk_percentage=_config.get("trading_risk_percentage")
                        or True,
                        trading_risk_amount=_config.get("trading_risk_amount") or 1,
                        trading_slippage=_config.get("trading_slippage") or 2,
                        trading_asset=_config.get("trading_asset") or "USDT",
                        trading_asset_separator=_config.get("trading_asset_separator")
                        or "",
                        mapping=_config.get("mapping") or [],
                    )
                    self.clients.append(client)
                    logger.debug(f"Loaded {item}")

        except Exception as e:
            logger.error("init: {}", e)

    def _create_client(self, **kwargs):
        """
        Get the handler object based on the specified platform.

        Returns:
            object: The handler object.
        """
        protocol = kwargs["protocol"]
        if protocol == "ccxt":
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
        version_info = f"{__version__}\n"
        client_info = "".join(
            f"💱 {client.name}\n🪪 {client.account}\n" for client in self.clients
        )
        return version_info + client_info.strip()

    async def get_quotes(self, symbol):
        """
        Return a list of quotes.

        Args:
            symbol

        Returns:
            quotes
        """

        quotes = []
        for cex in self.clients:
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
        for cex in self.clients:
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
        for _ in self.clients:
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
        for cex in self.clients:
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
        for cex in self.clients:
            try:
                trade = await cex.execute_order(order_params)
                order.append(trade)

            except Exception as e:
                logger.error("{} Error {}", cex.name, e)
                continue

        return order
