# """

# etrade client


# """

# import pyetrade

# from ._client import CexClient


# class FxcmHandler(CexClient):
#     """
#     library: https://github.com/jessecooper/pyetrade

#     Args:
#         None

#     Returns:
#         None

#     """

#     def __init__(
#         self,
#         **kwargs,
#     ):
#         """
#         Initialize the client

#         """
#         super().__init__(**kwargs)
#         self.client = pyetrade.ETradeAccounts(
#             self.api_key,
#             self.secret,
#             self.oauth_token,
#             self.oauth_token_secret,
#         )
#         self.account_data = self.client.list_accounts(resp_format="json")
#         self.account_number = self.account_data["Accounts"]["Account"][0]["accountId"]

#     async def get_quote(self, instrument):
#         """
#         Return a quote for a instrument


#         Args:
#             cex
#             instrument

#         Returns:
#             quote
#         """
#         return self.client.get_quote(symbols=[instrument], resp_format="json")

#     async def get_account_balance(self):
#         """
#         return account balance

#         Args:
#             None

#         Returns:
#             balance

#         """

#         return self.client.get_account_balance(account_id_key=self.account_number)

#     async def get_account_position(self):
#         """
#         Return account position.
#         of a given exchange

#         Args:
#             None

#         Returns:
#             position

#         """

#         return self.client.list_transactions(account_id_key=self.account_number)

#     async def get_trading_asset_balance(self):
#         """ """
#         return 0

#     async def execute_order(self, order_params):
#         """
#         Execute order

#         Args:
#             order_params (dict):
#                 action(str)
#                 instrument(str)
#                 quantity(int)

#         Returns:
#             trade_confirmation(dict)

#         """
#         pass
