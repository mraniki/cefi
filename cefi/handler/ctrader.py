# """

# cTrader client


# """

# from ctrader_open_api import Client
# from loguru import logger

# from .client import CexClient


# class CtraderHandler(CexClient):
#     """
#     CEX client
#     via openApiPy library
#     https://github.com/spotware/openApiPy

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
#         Initialize the ccxt client

#         """
#         super().__init__(**kwargs)
#         hostType = input("Host (Live/Demo): ")
#         host = EndPoints.PROTOBUF_LIVE_HOST
#         if hostType.lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST
#         client =

#         self.client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)


#     async def get_quote(self, instrument):
#         """
#         Return a quote for a instrument
#         of a given exchange ccxt object


#         Args:
#             cex
#             instrument

#         Returns:
#             quote
#         """
#         pass

#     async def get_account_balance(self):
#         """
#         return account balance of
#         a given ccxt exchange

#         Args:
#             None

#         Returns:
#             balance

#         """

#         return 0

#     async def get_account_position(self):
#         """
#         Return account position.
#         of a given exchange

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
