# """

# Degiro client


# """

# import ccxt
# from loguru import logger
# from degiro_connector.trading.api import API as TradingAPI
# from degiro_connector.trading.models.credentials import build_credentials
# from degiro_connector.trading.models.order import Action, Order, OrderType, TimeType
# from .client import CexClient


# class DegiroHandler(CexClient):
#     """
#     CEX client
#     via Degiro API
#     https://github.com/Chavithra/degiro-connector

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
#         if self.name is None:
#             return
#         client = TradingAPI(credentials=credentials)
#         client.connect()

#     async def get_quote(self, instrument):
#         """
#         Asynchronously fetches a ask/offer quote
#         for the specified instrument.

#         :param instrument: The instrument for which the quote is to be fetched.
#         :return: The fetched quote.
#         """
#         try:
#             instrument = await self.replace_instrument(instrument)

#             ticker = self.client.fetch_ticker(instrument)
#             quote = ticker["ask"]
#             logger.debug("Quote: {}", quote)
#             return quote
#         except Exception as e:
#             logger.error("{} Error {}", self.name, e)


#     async def get_account_balance(self):
#         """
#         return account balance of
#         a given ccxt exchange

#         Args:
#             None

#         Returns:
#             balance

#         """


#     async def get_account_position(self):
#         """
#         Return account position.
#         of a given exchange

#         Args:
#             None

#         Returns:
#             position

#         """



#     async def pre_order_checks(self, order_params):
#         """ """
#         return True

#     async def get_trading_asset_balance(self):
#         """ """
#         return self.client.fetchBalance()[f"{self.trading_asset}"]["free"]

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
#         try:
#             action = order_params.get("action")
#             instrument = await self.replace_instrument(order_params.get("instrument"))
#             quantity = order_params.get("quantity", self.trading_risk_amount)
#             logger.debug("quantity {}", quantity)
#             amount = await self.get_order_amount(
#                 quantity=quantity,
#                 instrument=instrument,
#                 is_percentage=self.trading_risk_percentage,
#             )
#             params = {
#                 "stopLoss": {
#                     "triggerPrice": order_params.get("stop_loss"),
#                     # "price": order_params.get("action") * 0.98,
#                 },
#                 "takeProfit": {
#                     "triggerPrice": order_params.get("take_profit"),
#                     # "price": order_params.get("action") * 0.98,
#                 },
#             }
#             logger.debug("amount {}", amount)
#             pre_order_checks = await self.pre_order_checks(order_params)
#             logger.debug("pre_order_checks {}", pre_order_checks)

#             if amount and pre_order_checks:
#                 if order := # PASS ORDER
# order = Order(
#     buy_sell=Action.BUY,
#     order_type=OrderType.LIMIT,
#     price=12.1,
#     product_id=72160,
#     size=1,
#     time_type=TimeType.GOOD_TILL_DAY,
# )

# checking_response = trading_api.check_order(order=order)
# print(checking_response)

# confirmation_response = trading_api.confirm_order(
#     confirmation_id=checking_response.confirmation_id,
#     order=order,
# )
# print(confirmation_response):
#                     return await self.get_trade_confirmation(order, instrument, action)
#             return f"Error executing {self.name}"

#         except Exception as e:
#             logger.error("{} Error {}", self.name, e)
#             return f"Error executing {self.name}"
