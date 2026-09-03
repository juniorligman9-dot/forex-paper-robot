"""
Demo market data feed for the Forex Paper Trading Robot.

This module generates simulated OHLCV candle data for paper-trading
development and testing. It does NOT provide real market prices.
"""

import hashlib
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from config import DATA_PROVIDER, TIMEFRAME


# Approximate starting prices used only for simulation
BASE_PRICES = {
    "EUR/USD": 1.0800,
    "GBP/USD": 1.2700,
    "USD/JPY": 150.00,
    "USD/CHF": 0.8800,
    "AUD/USD": 0.6600,
    "USD/CAD": 1.3500,
    "NZD/USD": 0.6100,

    "EUR/GBP": 0.8500,
    "EUR/JPY": 162.00,
    "EUR/CHF": 0.9500,
    "EUR/AUD": 1.6300,
    "EUR/CAD": 1.4600,
    "EUR/NZD": 1.7700,

    "GBP/JPY": 190.00,
    "GBP/CHF": 1.1200,
    "GBP/AUD": 1.9200,
    "GBP/CAD": 1.7200,
    "GBP/NZD": 2.0800,

    "AUD/JPY": 99.00,
    "AUD/CHF": 0.5800,
    "AUD/CAD": 0.8900,
    "AUD/NZD": 1.0800,

    "CAD/JPY": 111.00,
    "CAD/CHF": 0.6500,

    "CHF/JPY": 170.00,

    "NZD/JPY": 91.50,
    "NZD/CHF": 0.5400,
    "NZD/CAD": 0.8200,

    "USD/ZAR": 18.50,
    "USD/MXN": 17.00,
    "USD/TRY": 33.00,
    "USD/SEK": 10.50,
    "USD/NOK": 10.70,
    "USD/PLN": 4.00,
    "USD/HUF": 360.00,

    "EUR/ZAR": 20.00,
    "EUR/TRY": 36.00,

    "GBP/ZAR": 23.50,
}


def timeframe_to_frequency(timeframe):
    """
    Convert a trading timeframe into a pandas frequency.
    """

    mapping = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1h",
        "4h": "4h",
        "1d": "1D",
    }

    return mapping.get(timeframe, "1h")


class DataFeed:
    """
    Simulated Forex market data provider.

    Designed for testing the paper-trading robot before
    connecting to a real data provider.
    """

    def __init__(self):
        self.provider = DATA_PROVIDER
        self.timeframe = TIMEFRAME
        self.cache = {}

    @staticmethod
    def _get_seed(pair):
        """
        Create a stable random seed for each Forex pair.
        """

        pair_hash = hashlib.sha256(pair.encode()).hexdigest()
        return int(pair_hash[:8], 16)

    def get_candles(self, pair, limit=250):
        """
        Return simulated OHLCV candles.

        Parameters:
            pair (str): Forex pair, for example EUR/USD
            limit (int): Number of candles to return

        Returns:
            pandas.DataFrame
        """

        if not isinstance(pair, str):
            raise ValueError("Pair must be a string.")

        if limit < 50:
            limit = 50

        base_price = BASE_PRICES.get(pair, 1.0000)

        seed = self._get_seed(pair)
        rng = np.random.default_rng(seed)

        # Generate simulated percentage returns
        volatility = 0.002

        returns = rng.normal(
            loc=0.00002,
            scale=volatility,
            size=limit
        )

        close_prices = base_price * np.exp(
            np.cumsum(returns)
        )

        open_prices = np.empty(limit)
        open_prices[0] = base_price
        open_prices[1:] = close_prices[:-1]

        candle_range = np.abs(
            rng.normal(
                loc=0.001,
                scale=0.0005,
                size=limit
            )
        )

        high_prices = np.maximum(
            open_prices,
            close_prices
        ) * (1 + candle_range)

        low_prices = np.minimum(
            open_prices,
            close_prices
        ) * (1 - candle_range)

        volumes = rng.integers(
            low=100,
            high=1000,
            size=limit
        )

        frequency = timeframe_to_frequency(
            self.timeframe
        )

        timestamps = pd.date_range(
            end=datetime.now(timezone.utc),
            periods=limit,
            freq=frequency
        )

        data = pd.DataFrame({
            "timestamp": timestamps,
            "open": open_prices,
            "high": high_prices,
            "low": low_prices,
            "close": close_prices,
            "volume": volumes,
        })

        data["pair"] = pair

        self.cache[pair] = data

        return data.copy()

    def get_latest_price(self, pair):
        """
        Get the latest simulated closing price.
        """

        candles = self.get_candles(pair, limit=250)

        latest_price = float(
            candles["close"].iloc[-1]
        )

        return latest_price

    def get_multiple_pairs(self, pairs, limit=250):
        """
        Get candle data for multiple Forex pairs.

        Parameters:
            pairs (list): List of Forex pair strings
            limit (int): Number of candles per pair

        Returns:
            dict
        """

        market_data = {}

        for pair in pairs:
            try:
                market_data[pair] = self.get_candles(
                    pair,
                    limit
                )

            except Exception as error:
                print(
                    f"[DATA ERROR] "
                    f"Could not load {pair}: {error}"
                )

        return market_data


def create_data_feed():
    """
    Create and return a DataFeed instance.
    """

    return DataFeed()


if __name__ == "__main__":
    print("Forex Paper Robot - Demo Data Feed")
    print(f"Provider: {DATA_PROVIDER}")

    feed = create_data_feed()

    test_pair = "EUR/USD"

    candles = feed.get_candles(
        test_pair,
        limit=10
    )

    print(f"\nLatest data for {test_pair}:")
    print(candles)

    latest_price = feed.get_latest_price(
        test_pair
    )

    print(
        f"\nLatest simulated price: "
        f"{latest_price:.5f}"
    )
