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
