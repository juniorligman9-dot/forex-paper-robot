"""
Configuration settings for the Forex Paper Trading Robot.
"""

# =========================
# BOT SETTINGS
# =========================

BOT_NAME = "Forex Paper Robot"
PAPER_TRADING = True
DEBUG = True


# =========================
# PAPER ACCOUNT SETTINGS
# =========================

STARTING_BALANCE = 10000.00
ACCOUNT_CURRENCY = "USD"


# =========================
# FOREX PAIRS
# =========================

# Major Forex pairs
MAJOR_PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "USD/CHF",
    "AUD/USD",
    "USD/CAD",
    "NZD/USD",
]

# Popular minor/cross pairs
MINOR_PAIRS = [
    "EUR/GBP",
    "EUR/JPY",
    "EUR/CHF",
    "EUR/AUD",
    "EUR/CAD",
    "EUR/NZD",

    "GBP/JPY",
    "GBP/CHF",
    "GBP/AUD",
    "GBP/CAD",
    "GBP/NZD",

    "AUD/JPY",
    "AUD/CHF",
    "AUD/CAD",
    "AUD/NZD",

    "CAD/JPY",
    "CAD/CHF",

    "CHF/JPY",

    "NZD/JPY",
    "NZD/CHF",
    "NZD/CAD",
]

# Exotic pairs
EXOTIC_PAIRS = [
    "USD/ZAR",
    "USD/MXN",
    "USD/TRY",
    "USD/SEK",
    "USD/NOK",
    "USD/PLN",
    "USD/HUF",

    "EUR/ZAR",
    "EUR/TRY",

    "GBP/ZAR",
]

# All pairs scanned by the robot
FOREX_PAIRS = (
    MAJOR_PAIRS
    + MINOR_PAIRS
    + EXOTIC_PAIRS
)


# =========================
# TIMEFRAME SETTINGS
# =========================

TIMEFRAME = "1h"
CANDLE_LIMIT = 250


# =========================
# STRATEGY SETTINGS
# =========================

FAST_EMA_PERIOD = 20
SLOW_EMA_PERIOD = 50
RSI_PERIOD = 14

RSI_BUY_LEVEL = 55
RSI_SELL_LEVEL = 45


# =========================
# RISK MANAGEMENT
# =========================

RISK_PER_TRADE_PERCENT = 1.0
MAX_OPEN_TRADES = 5
MAX_TRADES_PER_DAY = 10

STOP_LOSS_PERCENT = 1.0
TAKE_PROFIT_PERCENT = 2.0


# =========================
# PAPER TRADING COSTS
# =========================

SIMULATED_SPREAD_PERCENT = 0.01
SIMULATED_SLIPPAGE_PERCENT = 0.005


# =========================
# BOT LOOP SETTINGS
# =========================

SCAN_INTERVAL_SECONDS = 60


# =========================
# DATA SOURCE
# =========================

DATA_PROVIDER = "demo"
