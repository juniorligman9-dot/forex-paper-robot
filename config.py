"""
Configuration for the Forex Paper Trading Robot.

Settings are loaded from the .env file.

IMPORTANT:
This project is configured for PAPER TRADING.
It does not place real trades.
"""

import os

from dotenv import load_dotenv


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_env_string(name, default=""):
    """
    Get a string value from the environment.
    """

    return os.getenv(
        name,
        default,
    )


def get_env_int(name, default=0):
    """
    Get an integer value from the environment.
    """

    try:
        return int(
            os.getenv(
                name,
                default,
            )
        )

    except (TypeError, ValueError):
        return int(default)


def get_env_float(name, default=0.0):
    """
    Get a float value from the environment.
    """

    try:
        return float(
            os.getenv(
                name,
                default,
            )
        )

    except (TypeError, ValueError):
        return float(default)


def get_env_bool(name, default=False):
    """
    Get a boolean value from the environment.

    Accepted True values:
    true, 1, yes, y, on
    """

    value = os.getenv(
        name,
        str(default),
    )

    return value.strip().lower() in [
        "true",
        "1",
        "yes",
        "y",
        "on",
    ]


# ==========================================
# BOT SETTINGS
# ==========================================

BOT_NAME = get_env_string(
    "BOT_NAME",
    "Forex Paper Trading Robot",
)

DEBUG = get_env_bool(
    "DEBUG",
    True,
)

PAPER_TRADING = get_env_bool(
    "PAPER_TRADING",
    True,
)


# ==========================================
# ACCOUNT SETTINGS
# ==========================================

STARTING_BALANCE = get_env_float(
    "STARTING_BALANCE",
    10000.0,
)

ACCOUNT_CURRENCY = get_env_string(
    "ACCOUNT_CURRENCY",
    "USD",
)


# ==========================================
# RISK MANAGEMENT
# ==========================================

RISK_PER_TRADE_PERCENT = (
    get_env_float(
        "RISK_PER_TRADE_PERCENT",
        1.0,
    )
)

MAX_OPEN_TRADES = get_env_int(
    "MAX_OPEN_TRADES",
    5,
)

MAX_TRADES_PER_DAY = get_env_int(
    "MAX_TRADES_PER_DAY",
    10,
)

STOP_LOSS_PERCENT = get_env_float(
    "STOP_LOSS_PERCENT",
    1.0,
)

TAKE_PROFIT_PERCENT = get_env_float(
    "TAKE_PROFIT_PERCENT",
    2.0,
)


# ==========================================
# MARKET DATA SETTINGS
# ==========================================

DATA_PROVIDER = get_env_string(
    "DATA_PROVIDER",
    "SIMULATED",
)

TIMEFRAME = get_env_string(
    "TIMEFRAME",
    "1h",
)

CANDLE_LIMIT = get_env_int(
    "CANDLE_LIMIT",
    250,
)


# ==========================================
# STRATEGY SETTINGS
# ==========================================

FAST_EMA_PERIOD = get_env_int(
    "FAST_EMA_PERIOD",
    9,
)

SLOW_EMA_PERIOD = get_env_int(
    "SLOW_EMA_PERIOD",
    21,
)

RSI_PERIOD = get_env_int(
    "RSI_PERIOD",
    14,
)

RSI_BUY_LEVEL = get_env_float(
    "RSI_BUY_LEVEL",
    55,
)

RSI_SELL_LEVEL = get_env_float(
    "RSI_SELL_LEVEL",
    45,
)


# ==========================================
# SIMULATED BROKER SETTINGS
# ==========================================

SIMULATED_SPREAD_PERCENT = (
    get_env_float(
        "SIMULATED_SPREAD_PERCENT",
        0.01,
    )
)

SIMULATED_SLIPPAGE_PERCENT = (
    get_env_float(
        "SIMULATED_SLIPPAGE_PERCENT",
        0.005,
    )
)


# ==========================================
# ROBOT SETTINGS
# ==========================================

SCAN_INTERVAL_SECONDS = get_env_int(
    "SCAN_INTERVAL_SECONDS",
    30,
)


# ==========================================
# FOREX PAIRS
# ==========================================

FOREX_PAIRS = [

    # Major pairs
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "USD/CHF",
    "AUD/USD",
    "USD/CAD",
    "NZD/USD",

    # EUR crosses
    "EUR/GBP",
    "EUR/JPY",
    "EUR/CHF",
    "EUR/AUD",
    "EUR/CAD",
    "EUR/NZD",

    # GBP crosses
    "GBP/JPY",
    "GBP/CHF",
    "GBP/AUD",
    "GBP/CAD",
    "GBP/NZD",

    # AUD crosses
    "AUD/JPY",
    "AUD/CHF",
    "AUD/CAD",
    "AUD/NZD",

    # CAD crosses
    "CAD/JPY",
    "CAD/CHF",

    # CHF crosses
    "CHF/JPY",

    # NZD crosses
    "NZD/JPY",
    "NZD/CHF",
    "NZD/CAD",

    # Exotic pairs
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


# ==========================================
# VALIDATION
# ==========================================

def validate_config():
    """
    Validate important configuration values.
    """

    if STARTING_BALANCE <= 0:
        raise ValueError(
            "STARTING_BALANCE must be "
            "greater than zero."
        )

    if RISK_PER_TRADE_PERCENT <= 0:
        raise ValueError(
            "RISK_PER_TRADE_PERCENT must "
            "be greater than zero."
        )

    if MAX_OPEN_TRADES <= 0:
        raise ValueError(
            "MAX_OPEN_TRADES must be "
            "greater than zero."
        )

    if MAX_TRADES_PER_DAY <= 0:
        raise ValueError(
            "MAX_TRADES_PER_DAY must be "
            "greater than zero."
        )

    if STOP_LOSS_PERCENT <= 0:
        raise ValueError(
            "STOP_LOSS_PERCENT must be "
            "greater than zero."
        )

    if TAKE_PROFIT_PERCENT <= 0:
        raise ValueError(
            "TAKE_PROFIT_PERCENT must be "
            "greater than zero."
        )

    if FAST_EMA_PERIOD <= 0:
        raise ValueError(
            "FAST_EMA_PERIOD must be "
            "greater than zero."
        )

    if SLOW_EMA_PERIOD <= 0:
        raise ValueError(
            "SLOW_EMA_PERIOD must be "
            "greater than zero."
        )

    if FAST_EMA_PERIOD >= SLOW_EMA_PERIOD:
        raise ValueError(
            "FAST_EMA_PERIOD should be "
            "smaller than SLOW_EMA_PERIOD."
        )

    if RSI_PERIOD <= 0:
        raise ValueError(
            "RSI_PERIOD must be "
            "greater than zero."
        )

    if RSI_SELL_LEVEL >= RSI_BUY_LEVEL:
        raise ValueError(
            "RSI_SELL_LEVEL must be lower "
            "than RSI_BUY_LEVEL."
        )

    if CANDLE_LIMIT < SLOW_EMA_PERIOD:
        raise ValueError(
            "CANDLE_LIMIT is too small for "
            "the configured EMA periods."
        )

    if SCAN_INTERVAL_SECONDS <= 0:
        raise ValueError(
            "SCAN_INTERVAL_SECONDS must be "
            "greater than zero."
        )

    return True


# Validate configuration when imported
validate_config()


# ==========================================
# CONFIGURATION SUMMARY
# ==========================================

def get_config_summary():
    """
    Return a safe configuration summary.

    No API keys or secrets are included.
    """

    return {
        "bot_name": BOT_NAME,
        "paper_trading": PAPER_TRADING,
        "data_provider": DATA_PROVIDER,
        "timeframe": TIMEFRAME,
        "forex_pairs": len(FOREX_PAIRS),
        "starting_balance": STARTING_BALANCE,
        "account_currency": ACCOUNT_CURRENCY,
        "risk_per_trade_percent": (
            RISK_PER_TRADE_PERCENT
        ),
        "max_open_trades": (
            MAX_OPEN_TRADES
        ),
        "max_trades_per_day": (
            MAX_TRADES_PER_DAY
        ),
        "scan_interval_seconds": (
            SCAN_INTERVAL_SECONDS
        ),
    }


if __name__ == "__main__":

    print("=" * 50)
    print("FOREX ROBOT CONFIGURATION")
    print("=" * 50)

    config = get_config_summary()

    for key, value in config.items():
        print(f"{key}: {value}")

    print("=" * 50)
    print("Configuration loaded successfully.")
