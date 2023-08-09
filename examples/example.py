"""
Provides example for FindMyOrder
"""

import asyncio
import sys

import uvicorn
from fastapi import FastAPI
from loguru import logger
from xxxxx import __version__, xxxxx

logger.remove()
logger.add(sys.stderr, level="DEBUG")

async def main():
    """Main"""


app = FastAPI()


@app.on_event("startup")
async def start():
    """startup"""
    asyncio.create_task(main())


@app.get("/")
def read_root():
    """root"""
    return {"FMO is online"}


@app.get("/health")
def health_check():
    """healthcheck"""
    return {"FMO is online"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
