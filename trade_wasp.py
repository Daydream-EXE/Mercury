"""TradeWASP - Phase 1: Foundation & Market Connectivity

This script connects to Binance exchange using the python-binance
library and streams live market data via WebSocket. Configuration and
API keys are stored in a separate config.ini file.
"""

import configparser
import json
import os
import sys
import time

from binance.client import Client
from binance.exceptions import BinanceAPIException
from websocket import WebSocketApp


class MarketDataConnector:
    """Handles Binance market data operations."""

    def __init__(self, api_key: str, api_secret: str) -> None:
        """Initialize the Binance client."""
        self.client = Client(api_key, api_secret)

    def test_connection(self) -> bool:
        """Ping server and check account status to verify connection."""
        try:
            self.client.ping()
            self.client.get_account()
        except BinanceAPIException as err:
            print(f"Connection test failed: {err}")
            return False
        except Exception as err:  # Generic catch for network issues
            print(f"Connection test failed: {err}")
            return False

        print("Connection successful and authenticated.")
        return True

    def get_order_book(self, symbol: str) -> None:
        """Fetch and display the top 5 bids and asks for the symbol."""
        depth = self.client.get_order_book(symbol=symbol, limit=5)
        print(f"Order book for {symbol}:")
        print("Bids:")
        for price, qty in depth.get("bids", []):
            print(f"  Price: {price} Qty: {qty}")
        print("Asks:")
        for price, qty in depth.get("asks", []):
            print(f"  Price: {price} Qty: {qty}")

    def get_recent_trades(self, symbol: str) -> None:
        """Fetch and display the 10 most recent trades for the symbol."""
        trades = self.client.get_recent_trades(symbol=symbol, limit=10)
        print(f"Recent trades for {symbol}:")
        for trade in trades:
            price = trade.get("price")
            qty = trade.get("qty")
            timestamp = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(trade.get("time") / 1000)
            )
            print(f"  Price: {price} Qty: {qty} Time: {timestamp}")


def on_open(ws: WebSocketApp) -> None:
    """Callback for when the WebSocket connection is opened."""
    print("WebSocket connection opened.")


def on_message(ws: WebSocketApp, message: str) -> None:
    """Handle incoming WebSocket messages."""
    data = json.loads(message)
    if "data" in data:
        payload = data["data"]
        symbol = payload.get("s")
        close = payload.get("c")
        volume = payload.get("v")
        print(f"{symbol} | Close: {close} | Volume: {volume}")


def on_close(ws: WebSocketApp, close_status_code, close_msg) -> None:
    """Callback for when the WebSocket connection is closed."""
    print("WebSocket connection closed.")


def load_config(path: str) -> tuple[str, str]:
    """Load API keys from the config.ini file."""
    config = configparser.ConfigParser()
    if not os.path.exists(path):
        config["binance"] = {"api_key": "YOUR_API_KEY", "api_secret": "YOUR_API_SECRET"}
        with open(path, "w") as f:
            config.write(f)
        print(f"Created placeholder config at {path}. Please add your API keys.")
        return "", ""

    config.read(path)
    api_key = config.get("binance", "api_key", fallback="")
    api_secret = config.get("binance", "api_secret", fallback="")
    return api_key, api_secret


if __name__ == "__main__":
    CONFIG_PATH = "config.ini"
    API_KEY, API_SECRET = load_config(CONFIG_PATH)

    if not API_KEY or not API_SECRET or API_KEY == "YOUR_API_KEY":
        print("Error: API keys not configured in config.ini. Exiting.")
        sys.exit(1)

    connector = MarketDataConnector(API_KEY, API_SECRET)
    if not connector.test_connection():
        sys.exit(1)

    symbol = "BTCUSDT"
    connector.get_order_book(symbol)
    connector.get_recent_trades(symbol)

    stream_url = (
        "wss://stream.binance.com:9443/stream?streams="
        "btcusdt@ticker/ethusdt@ticker/dogeusdt@ticker"
    )

    ws = WebSocketApp(stream_url, on_open=on_open, on_message=on_message, on_close=on_close)
    ws.run_forever()
