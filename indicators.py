"""
Technical indicators for the Forex Paper Trading Robot.
"""

import numpy as np
import pandas as pd


def validate_dataframe(data):
    """
    Validate that the input is a pandas DataFrame.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            "Data must be a pandas DataFrame."
        )

    if data.empty:
        raise ValueError(
            "DataFrame cannot be empty."
        )


def ema(series, period):
    """
    Calculate the Exponential Moving Average (EMA).

    Parameters:
        series (pandas.Series): Price data
        period (int): EMA period

    Returns:
        pandas.Series
    """

    if period <= 0:
        raise ValueError(
            "EMA period must be greater than zero."
        )

    return series.ewm(
        span=period,
        adjust=False
    ).mean()


def sma(series, period):
    """
    Calculate the Simple Moving Average (SMA).
    """

    if period <= 0:
        raise ValueError(
            "SMA period must be greater than zero."
        )

    return series.rolling(
        window=period,
        min_periods=period
    ).mean()


def rsi(series, period=14):
    """
    Calculate the Relative Strength Index (RSI).

    Parameters:
        series (pandas.Series): Closing prices
        period (int): RSI period

    Returns:
        pandas.Series
    """

    if period <= 0:
        raise ValueError(
            "RSI period must be greater than zero."
        )

    delta = series.diff()

    gains = delta.clip(
        lower=0
    )

    losses = -delta.clip(
        upper=0
    )

    average_gain = gains.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    average_loss = losses.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    # Avoid division by zero
    relative_strength = average_gain / average_loss.replace(
        0,
        np.nan
    )

    rsi_values = 100 - (
        100 / (
            1 + relative_strength
        )
    )

    # Handle periods where there are only gains
    rsi_values = rsi_values.where(
        average_loss != 0,
        100
    )

    # Handle periods where there are only losses
    rsi_values = rsi_values.where(
        average_gain != 0,
        0
    )

    return rsi_values


def atr(data, period=14):
    """
    Calculate the Average True Range (ATR).

    Required columns:
        high
        low
        close
    """

    validate_dataframe(data)

    required_columns = [
        "high",
        "low",
        "close",
    ]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    previous_close = data["close"].shift(1)

    high_low = (
        data["high"] - data["low"]
    )

    high_previous_close = (
        data["high"] - previous_close
    ).abs()

    low_previous_close = (
        data["low"] - previous_close
    ).abs()

    true_range = pd.concat(
        [
            high_low,
            high_previous_close,
            low_previous_close,
        ],
        axis=1
    ).max(axis=1)

    return true_range.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()


def macd(
    series,
    fast_period=12,
    slow_period=26,
    signal_period=9
):
    """
    Calculate MACD, signal line, and histogram.

    Returns:
        pandas.DataFrame
    """

    if fast_period <= 0:
        raise ValueError(
            "Fast period must be greater than zero."
        )

    if slow_period <= fast_period:
        raise ValueError(
            "Slow period must be greater than "
            "the fast period."
        )

    fast_ema = ema(
        series,
        fast_period
    )

    slow_ema = ema(
        series,
        slow_period
    )

    macd_line = (
        fast_ema - slow_ema
    )

    signal_line = ema(
        macd_line,
        signal_period
    )

    histogram = (
        macd_line - signal_line
    )

    return pd.DataFrame({
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram,
    })


def bollinger_bands(
    series,
    period=20,
    standard_deviations=2
):
    """
    Calculate Bollinger Bands.

    Returns:
        pandas.DataFrame
    """

    if period <= 0:
        raise ValueError(
            "Period must be greater than zero."
        )

    middle_band = sma(
        series,
        period
    )

    standard_deviation = series.rolling(
        window=period,
        min_periods=period
    ).std()

    upper_band = (
        middle_band
        + standard_deviations
        * standard_deviation
    )

    lower_band = (
        middle_band
        - standard_deviations
        * standard_deviation
    )

    return pd.DataFrame({
        "upper": upper_band,
        "middle": middle_band,
        "lower": lower_band,
    })


def add_indicators(
    data,
    fast_ema_period=20,
    slow_ema_period=50,
    rsi_period=14
):
    """
    Add the main technical indicators
    to a copy of the price DataFrame.

    Required column:
        close

    Returns:
        pandas.DataFrame
    """

    validate_dataframe(data)

    if "close" not in data.columns:
        raise ValueError(
            "Missing required column: close"
        )

    result = data.copy()

    result["ema_fast"] = ema(
        result["close"],
        fast_ema_period
    )

    result["ema_slow"] = ema(
        result["close"],
        slow_ema_period
    )

    result["rsi"] = rsi(
        result["close"],
        rsi_period
    )

    # ATR requires high, low and close
    if all(
        column in result.columns
        for column in [
            "high",
            "low",
            "close",
        ]
    ):
        result["atr"] = atr(
            result,
            period=14
        )

    return result


if __name__ == "__main__":
    print(
        "Testing Forex Technical Indicators"
    )

    test_data = pd.DataFrame({
        "close": np.linspace(
            1.0800,
            1.1000,
            100
        )
        + np.random.normal(
            0,
            0.002,
            100
        )
    })

    test_data["high"] = (
        test_data["close"] * 1.002
    )

    test_data["low"] = (
        test_data["close"] * 0.998
    )

    results = add_indicators(
        test_data
    )

    print(
        results.tail()
    )
