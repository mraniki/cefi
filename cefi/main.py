from loguru import logger

from cefi import __version__

from .config import settings
from .protocol import CexCcxt, CexIB


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
                if item in ["", "template"]:
                    continue
                client = self._create_client(
                    protocol=_config.get("protocol") or "ccxt",
                    name=_config.get("name"),
                    host=_config.get("host") or "127.0.0.1",
                    port=_config.get("port") or  7497,
                    user_id=_config.get("user_id") or "",
                    api_key=_config.get("api_key"),
                    secret=_config.get("secret") or "",
                    password=_config.get("password") or "",
                    testmode=_config.get("testmode") or False,
                    broker_client_id=_config.get("broker_client_id") or 1,
                    broker_account_number=_config.get("broker_account_number") or "",
                    broker_gateway=_config.get("broker_gateway") or True,
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
                if client.client:
                    self.clients.append(client)
                    logger.debug(f"Loaded {item}")
            if self.clients:
                logger.info(f"Loaded {len(self.clients)} CEX clients")
            else:
                logger.warning("No CEX clients loaded. Verify config")

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
        elif protocol == "ib":
            return CexIB(**kwargs)
        else:
            logger.error("Invalid platform {}", protocol)

    async def get_info(self):
        """
        Retrieves information about the exchange
        and the account.

        :return: A formatted string containing
        the exchange name and the account information.
        :rtype: str
        """
        version_info = f"ℹ️ {type(self).__name__} {__version__}\n"
        client_info = "".join(
            f"💱 {client.name} {client.account_number}\n" for client in self.clients
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
        _info = ["⚖️\n"]
        for client in self.clients:
            _info.append(f"{client.name}: {await client.get_quote(symbol)}")
        return "\n".join(_info)

    async def get_balances(self):
        """
        Return account balance.

        Args:
            None

        Returns:
            balance

        """
        _info = ["💵\n"]
        for client in self.clients:
            _info.append(f"{client.name}:\n{await client.get_account_balance()}")
        return "\n".join(_info)

    async def get_positions(self):
        """
        return account position.

        Args:
            None

        Returns:
            position

        """
        _info = ["📊\n"]
        for client in self.clients:
            _info.append(f"{client.name}:\n{await client.get_account_position()}")
        return "\n".join(_info)

    async def get_pnls(self):
        """
        Return account pnl.

        Args:
            None

        Returns:
            pnl
        """
        _info = ["📊\n"]
        for client in self.clients:
            _info.append(f"{client.name}:\n{await client.get_account_pnl()}")
        return "\n".join(_info)

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
        for client in self.clients:
            try:
                trade = await client.execute_order(order_params)
                order.append(trade)
            except Exception as e:
                logger.error("submit_order - client {} error {}", client.name, e)
        return order
