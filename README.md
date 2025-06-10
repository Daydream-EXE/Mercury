# Mercury

## TradeWASP - Phase 1

This repository contains a simple demonstration script for connecting to
Binance and streaming live market data. The script is implemented in
`trade_wasp.py` and requires API keys stored in a `config.ini` file.

### Usage
1. Install dependencies:
   ```bash
   pip install python-binance websocket-client
   ```
2. Run the script:
   ```bash
   python trade_wasp.py
   ```
The script will create a `config.ini` file with placeholder keys if it
   does not exist. Replace the placeholders with your Binance API key and
   secret, then run the script again.

## TradeWASP - Phase 2

The `backtester.py` module provides a simple dual moving average
crossover backtesting engine. It uses historical data stored in a CSV
file.

### Preparing Historical Data
Download 1-hour candlestick data for `BTCUSDT` from Binance and save it
as `BTCUSDT_1h.csv` with the following columns:
`timestamp`, `open`, `high`, `low`, `close`, `volume`.

### Running the Backtest
1. Install dependencies:
   ```bash
   pip install pandas
   ```
2. Execute the backtester:
   ```bash
   python backtester.py
   ```
