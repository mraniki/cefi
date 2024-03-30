"""

CEFI Main 🤖

"""

import importlib

from loguru import logger

from cefi import __version__
from cefi.config import settings


class CexTrader:
    """
    CEX Object to support multiple
    centralized exchanges and broker APIs.

    Args:
        None

    Returns:
        None

    Methods:

        _create_client(self, **kwargs)
        get_all_client_classes(self)
        get_info(self)
        get_quotes(self, symbol)
        get_balances(self)
        get_positions(self)
        get_pnls(self)
        submit_order(self, order_params)

    """

    def __init__(self):
        """
        Initializes the class instance by creating and appending clients
        based on the configuration in `settings.cex`.

        Checks if the module is enabled by looking at `settings.myllm_enabled`.
        If the module is disabled, no clients will be created.

        Creates a mapping of library names to client classes.
        This mapping is used to create new clients based on the configuration.

        If a client's configuration exists in `settings.cex_enabled` and is truthy,
        it will be created.
        Clients are not created if their name is "template" or empty string.

        If a client is successfully created, it is appended to the `clients` list.

        If a client fails to be created, a message is logged with the name of the
        client and the error that occurred.

        Parameters:
            None

        Returns:
            None
        """
        # Check if the module is enabled
        self.enabled = settings.cex_enabled or True

        # Create a mapping of library names to client classes
        self.client_classes = self.get_all_client_classes()
        # logger.debug("client_classes available {}", self.client_classes)

        if not self.enabled:
            logger.info("Module is disabled. No clients will be created.")
            return
        self.clients = []
        # Create a client for each client in settings.myllm
        for name, client_config in settings.cex.items():
            # Skip template and empty string client names
            if name in ["", "template"] or not client_config.get("enabled"):
                continue
            try:
                # Create the client
                client = self._create_client(**client_config, name=name)
                # If the client has a valid client attribute, append it to the list
                if client and getattr(client, "client", None):
                    self.clients.append(client)
            except Exception as e:
                # Log the error if the client fails to be created
                logger.error(f"Failed to create client {name}: {e}")

        # Log the number of clients that were created
        logger.info(f"Loaded {len(self.clients)} clients")
        if not self.clients:
            logger.warning(
                """
                No clients were created.
                Check your settings or disable the module.
                https://talky.readthedocs.io/en/latest/02_config.html
                """
            )

    def _create_client(self, **kwargs):
        """
        Create a client based on the given protocol.

        This function takes in a dictionary of keyword arguments, `kwargs`,
        containing the necessary information to create a client. The required
        key in `kwargs` is "library", which specifies the protocol to use for
        communication with the LLM. The value of "library" must match one of the
        libraries supported by MyLLM.

        This function retrieves the class used to create the client based on the
        value of "library" from the mapping of library names to client classes
        stored in `self.client_classes`. If the value of "library" does not
        match any of the libraries supported, the function logs an error message
        and returns None.

        If the class used to create the client is found, the function creates a
        new instance of the class using the keyword arguments in `kwargs` and
        returns it.

        The function returns a client object based on the specified protocol
        or None if the library is not supported.

        Parameters:
            **kwargs (dict): A dictionary of keyword arguments containing the
            necessary information for creating the client. The required key is
            "library".

        Returns:
            A client object based on the specified protocol or None if the
            library is not supported.

        """

        library = kwargs.get("protocol") or kwargs.get("library")
        client_class = self.client_classes.get(f"{library.capitalize()}Handler")

        if client_class is None:
            logger.error(f"library {library} not supported")
            return None

        return client_class(**kwargs)

    def get_all_client_classes(self):
        """
        Retrieves all client classes from the `myllm.provider` module.

        This function imports the `myllm.provider` module and retrieves
        all the classes defined in it.

        The function returns a dictionary where the keys are the
        names of the classes and the values are the corresponding
        class objects.

        Returns:
            dict: A dictionary containing all the client classes
            from the `myllm.provider` module.
        """
        provider_module = importlib.import_module("cefi.handler")
        return {
            name: cls
            for name, cls in provider_module.__dict__.items()
            if isinstance(cls, type)
        }

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
