# News-Driven Forex Trading Bot

A Python-based news-driven Forex trading bot that analyzes financial market news, generates trading signals, applies risk management rules, and executes demo trades through MetaTrader 5.

## Overview

This project is designed to explore automated trading based primarily on financial news and market sentiment.

The bot monitors several financial instruments:

- EURUSD
- GBPUSD
- USDJPY
- XAUUSD (Gold)
- USOIL (WTI Crude Oil)

The system analyzes available market news and assigns directional scores and confidence levels to each market. It then selects the strongest trading opportunity and performs a risk check before placing a demo trade.

## Main Features

- Financial news analysis
- Market sentiment analysis
- News-based BUY / SELL / HOLD signals
- Opportunity ranking
- Confidence scoring
- MetaTrader 5 integration
- Automatic market symbol detection
- Position limit protection
- Daily loss protection
- Risk-per-trade management
- Automatic Stop Loss calculation
- Automatic Take Profit calculation
- Risk/Reward management
- Trade logging
- CSV trade history
- Backtesting components
- Performance reporting
- Equity curve visualization
- Demo trading

## Trading Workflow

The bot follows this general workflow:

1. Connect to MetaTrader 5.
2. Detect available broker symbols.
3. Collect and analyze relevant market news.
4. Calculate news sentiment and directional effects.
5. Generate BUY, SELL, or HOLD signals.
6. Rank the available opportunities.
7. Select the strongest opportunity.
8. Check risk and open-position limits.
9. Calculate position size based on account risk.
10. Calculate Stop Loss and Take Profit.
11. Send a demo order through MetaTrader 5.
12. Save the executed trade to the trade log.

## Risk Management

The current demo configuration uses:

- Risk per trade: 1%
- Target risk/reward: 1:2
- Maximum daily loss: 2%
- Maximum open positions: 1

Position size is calculated using the instrument's MetaTrader 5 tick size and tick value rather than using a fixed lot size.

This allows the position size to adapt to different instruments such as Forex pairs and Gold.

## Project Structure

```text
news-driven-forex-trading-bot/
│
├── config/
│   └── assets.json
│
├── data/
│   ├── forex_prices.csv
│   ├── forex_test_data.csv
│   └── trades.csv
│
├── reports/
│   ├── backtest_report.txt
│   └── equity_curve.png
│
├── src/
│   ├── main.py
│   ├── news_analyzer.py
│   ├── order_manager.py
│   ├── risk_guard.py
│   ├── risk_manager.py
│   ├── strategy.py
│   ├── market_analyzer.py
│   ├── indicators.py
│   ├── data_collector.py
│   ├── backtester.py
│   ├── performance.py
│   ├── report.py
│   ├── trade_logger.py
│   └── trade_visualizer.py
│
├── requirements.txt
├── .gitignore
└── README.md