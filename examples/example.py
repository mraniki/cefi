"""
Provides example for CEX lib
"""

import asyncio

from cefi import CexTrader


async def main():
    """Main"""
    cex = CexTrader()

    balance = await cex.get_balances()
    print("balance ", balance)

    # symbol = "BTC"
    # quote = await cex.get_quotes(symbol)
    # print("quote ", quote)
    # # quote  ⚖️
    # # binance: 69730.15
    # # capital: 69674.55

    # order = {
    #     "action": "BUY",
    #     "instrument": "BTC",
    #     "quantity": 1,
    # }
    # order = await cex.submit_order(order)
    # print("order ", order)


if __name__ == "__main__":
    asyncio.run(main())
