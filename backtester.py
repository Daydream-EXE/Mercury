"""Backtesting engine for TradeWASP - Phase 2.

This script implements a simple dual moving average crossover strategy.
It loads historical data from a CSV file and simulates trades while
accounting for transaction fees.

The expected CSV format is:
```
timestamp,open,high,low,close,volume
```
One row per 1-hour candle. You can obtain this data from Binance using
its kline REST API or data download service and save it as
`BTCUSDT_1h.csv` in the same directory as this script.
"""

from __future__ import annotations

import os
import pandas as pd


class Backtester:
    """Simple dual moving average backtester."""

    def __init__(self, symbol: str, data: pd.DataFrame,
                 initial_capital: float, transaction_fee_percent: float) -> None:
        self.symbol = symbol
        self.data = data
        self.initial_capital = initial_capital
        self.transaction_fee_percent = transaction_fee_percent
        self.cash = initial_capital
        self.shares = 0.0
        self.position = False  # holding or not
        self.portfolio_values: list[float] = []
        self.trades: list[dict] = []
        self._entry_price = 0.0
        self._entry_fee = 0.0

    def run_backtest(self, short_window: int, long_window: int) -> None:
        """Execute the backtest over historical data."""
        prev_diff = None
        closes = self.data["close"].tolist()

        for i, price in enumerate(closes):
            if i + 1 < long_window:
                # not enough data for long SMA yet
                self.portfolio_values.append(self.cash + self.shares * price)
                continue

            sma_short = sum(closes[max(0, i - short_window + 1): i + 1]) / short_window
            sma_long = sum(closes[i - long_window + 1: i + 1]) / long_window
            diff = sma_short - sma_long

            if prev_diff is not None:
                if diff > 0 >= prev_diff and not self.position:
                    self._execute_trade("BUY", price)
                elif diff < 0 <= prev_diff and self.position:
                    self._execute_trade("SELL", price)
            prev_diff = diff
            # record portfolio value
            value = self.cash + self.shares * price
            self.portfolio_values.append(value)

        # close any open position at last price
        if self.position:
            self._execute_trade("SELL", closes[-1])
            self.portfolio_values[-1] = self.cash

    def _execute_trade(self, signal: str, price: float) -> None:
        fee_rate = self.transaction_fee_percent / 100.0
        if signal == "BUY":
            qty = self.cash / price
            if qty <= 0:
                return
            cost = qty * price
            fee = cost * fee_rate
            self.cash -= cost + fee
            self.shares += qty
            self.position = True
            self._entry_price = price
            self._entry_fee = fee
            self.trades.append({"signal": "BUY", "price": price, "qty": qty, "fee": fee})
        elif signal == "SELL" and self.shares > 0:
            proceeds = self.shares * price
            fee = proceeds * fee_rate
            self.cash += proceeds - fee
            profit = (price - self._entry_price) * self.shares - fee - self._entry_fee
            self.trades.append({
                "signal": "SELL",
                "price": price,
                "qty": self.shares,
                "fee": fee,
                "profit": profit
            })
            self.shares = 0.0
            self.position = False

    def generate_report(self) -> None:
        final_value = self.cash + self.shares * self.data["close"].iloc[-1]
        net_profit = final_value - self.initial_capital
        net_profit_pct = (net_profit / self.initial_capital) * 100
        trade_count = len([t for t in self.trades if t["signal"] == "SELL"])
        wins = len([t for t in self.trades if t.get("profit", 0) > 0])
        win_rate = (wins / trade_count * 100) if trade_count else 0

        peak = self.portfolio_values[0] if self.portfolio_values else self.initial_capital
        max_drawdown = 0.0
        running_max = peak
        for value in self.portfolio_values:
            if value > running_max:
                running_max = value
            drawdown = (running_max - value) / running_max
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        max_drawdown_pct = max_drawdown * 100

        print("\nBacktest Report")
        print("---------------")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Portfolio Value: ${final_value:,.2f}")
        print(f"Net Profit: ${net_profit:,.2f} ({net_profit_pct:.2f}%)")
        print(f"Total Trades Executed: {trade_count}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Maximum Drawdown: {max_drawdown_pct:.2f}%")


if __name__ == "__main__":
    CSV_FILE = "BTCUSDT_1h.csv"
    if not os.path.exists(CSV_FILE):
        print(f"Historical data file '{CSV_FILE}' not found.")
        print("Download 1h klines from Binance and save them as this file before running.")
        raise SystemExit(1)

    df = pd.read_csv(CSV_FILE)
    required_columns = {"timestamp", "open", "high", "low", "close", "volume"}
    if not required_columns.issubset(df.columns):
        print("CSV file is missing required columns. Expected:", ", ".join(required_columns))
        raise SystemExit(1)

    backtester = Backtester("BTCUSDT", df, initial_capital=1000.0, transaction_fee_percent=0.1)
    backtester.run_backtest(short_window=50, long_window=200)
    backtester.generate_report()
