import ccxt
from loguru import logger

from cefi.config import settings


class CexClient:
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
        Initialize the Cex object

        """

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

    async def get_account_position(self, cx_client):
        """
        Return account position.
        of a given exchange

        Args:
            None

        Returns:
            position

        """

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
        # TODO implement mapping
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
                logger.debug("quantity {}", quantity)
                transaction_amount = (
                    asset_out_balance * (float(quantity) / 100) / asset_out_quote
                )
                logger.debug("transaction_amount {}", transaction_amount)

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

    async def replace_instrument(self, instrument):
        """
        Replace instrument by an alternative instrument, if the
        instrument is not in the mapping, it will be ignored.

        Args:
            order (dict):

        Returns:
            dict
        """
        for item in self.mapping:
            if item["id"] == instrument:
                instrument = item["alt"]
                self.logger.debug("Instrument symbol changed", instrument)
                break

        return instrument
