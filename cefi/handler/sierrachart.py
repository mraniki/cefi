# """

# Sierrachart client


# """


# from loguru import logger

# from .client import CexClient


# class SierrachartHandler(CexClient):
#     """
#     library:https://github.com/jseparovic/python-ws-dtc-client

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


#     async def get_quote(self, instrument):
#         """
#         Return a quote for a instrument

#         Args:
#             cex
#             instrument

#         Returns:
#             quote
#         """
#         pass

#     async def get_account_balance(self):
#         """
#         return account balance 

#         Args:
#             None

#         Returns:
#             balance

#         """

#         return 0

#     async def get_account_position(self):
#         """
#         Return account position.

#         Args:
#             None

#         Returns:
#             position

#         """


#         return 0

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