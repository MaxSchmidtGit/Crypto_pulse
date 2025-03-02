# Crypto_pulse

CryptoPulse is a modular, Python-based crypto trading bot that exclusively uses public API endpoints (e.g., from Binance) so that no sensitive API keys are required. This project demonstrates advanced trading strategies using multiple technical indicators and dynamic risk management features.

## Overview

CryptoPulse combines several technical indicators—including RSI, MACD, Bollinger Bands, Fibonacci retracement levels, and a simple order book indicator—to generate weighted signals that trigger buy, sell, or hold decisions. Additionally, the bot dynamically calculates stop-loss and take-profit levels based on an ATR proxy, enhancing risk management.

## Features

- **Public API Usage:** No need for private API keys; uses publicly accessible endpoints.
- **Advanced Indicators:**
  - **RSI (Relative Strength Index)**
  - **MACD (Moving Average Convergence Divergence)**
  - **Bollinger Bands**
  - **Fibonacci Retracement Levels**
  - **Order Book Indicator (simulated)**
- **Weighted Signal Combination:** Each indicator casts a vote (1 for buy, -1 for sell, or 0 for hold) which is weighted to form an overall signal.
- **Dynamic Risk Management:** Calculates stop-loss and take-profit levels based on the Average True Range (ATR) of the last 14 prices.
- **Simple Backtesting Function:** Allows you to evaluate the strategy using historical price data.

## Requirements

- Python 3.7 or higher
- Required Python packages (e.g., `numpy`, `requests`)
