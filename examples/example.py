"""
Provides example for CEX lib
"""

import asyncio

from cefi import CexTrader


async def main():
    """Main"""
    cex = CexTrader()
    await cex.get_account_balances()


if __name__ == "__main__":
    asyncio.run(main())
