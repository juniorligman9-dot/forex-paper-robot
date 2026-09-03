"""
Dynamic simulated market data feed for the Forex Paper Trading Robot.

This module creates evolving simulated OHLCV data.

Features:
- Persistent prices while the robot is running
- Prices change on every update
- Historical candles evolve over time
- Different volatility for different Forex pairs
- Supports paper-trading development and testing

IMPORTANT:
This is simulated market data.
It does NOT provide real Forex prices.
"""

import hashlib
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from config import DATA_PROVIDER, TIMEFRAME


# ==========================================
# BASE PRICES
# ==========================================

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


# ==========================================
# TIMEFRAME CONVERSION
# ==========================================

def timeframe_to_frequency(timeframe):
    """
    Convert trading timeframe to a pandas
    date frequency.
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

    return mapping.get(
        timeframe,
        "1h"
    )


# ==========================================
# DATA FEED
# ==========================================

class DataFeed:
    """
    Dynamic simulated Forex market data provider.

    Prices and candles remain in memory and
    evolve each time update_market() is called.
    """

    def __init__(self):
        self.provider = DATA_PROVIDER
        self.timeframe = TIMEFRAME

        # Stores historical candles
        self.market_data = {}

        # Stores current prices
        self.current_prices = {}

        # Random number generator
        self.rng = np.random.default_rng()

        # Number of market updates
        self.update_count = 0

    # --------------------------------------
    # PAIR SETTINGS
    # --------------------------------------

    def get_pair_volatility(self, pair):
        """
        Return simulated volatility based
        on the type of Forex pair.
        """

        # Exotic pairs generally move more
        exotic_currencies = [
            "ZAR",
            "MXN",
            "TRY",
            "SEK",
            "NOK",
            "PLN",
            "HUF",
        ]

        if any(
            currency in pair
            for currency in exotic_currencies
        ):
            return 0.0030

        # JPY crosses can be moderately volatile
        if "JPY" in pair:
            return 0.0020

        # Default volatility
        return 0.0015

    def get_pair_trend(self, pair):
        """
        Create a small changing trend.

        The trend changes gradually as the
        simulation runs.
        """

        pair_hash = hashlib.sha256(
            pair.encode()
        ).hexdigest()

        seed_value = int(
            pair_hash[:8],
            16
        )

        # Creates different behaviour per pair
        cycle = (
            np.sin(
                (
                    self.update_count
                    + seed_value % 50
                )
                / 15
            )
        )

        return cycle * 0.0003

    # --------------------------------------
    # INITIALIZATION
    # --------------------------------------

    def initialize_pair(
        self,
        pair,
        limit=250,
    ):
        """
        Create initial historical candle data
        for a Forex pair.
        """

        if pair in self.market_data:
            return

        if limit < 100:
            limit = 100

        base_price = BASE_PRICES.get(
            pair,
            1.0000
        )

        volatility = (
            self.get_pair_volatility(pair)
        )

        # Each pair receives a stable
        # initial historical pattern.
        pair_hash = hashlib.sha256(
            pair.encode()
        ).hexdigest()

        seed = int(
            pair_hash[:8],
            16
        )

        pair_rng = np.random.default_rng(
            seed
        )

        # Create initial market returns
        returns = pair_rng.normal(
            loc=0.00001,
            scale=volatility,
            size=limit,
        )

        close_prices = (
            base_price
            * np.exp(
                np.cumsum(returns)
            )
        )

        # Start the first candle at base price
        open_prices = np.empty(limit)

        open_prices[0] = base_price

        open_prices[1:] = (
            close_prices[:-1]
        )

        # Candle ranges
        ranges = np.abs(
            pair_rng.normal(
                loc=volatility * 0.7,
                scale=volatility * 0.3,
                size=limit,
            )
        )

        high_prices = (
            np.maximum(
                open_prices,
                close_prices,
            )
            * (1 + ranges)
        )

        low_prices = (
            np.minimum(
                open_prices,
                close_prices,
            )
            * (1 - ranges)
        )

        volumes = pair_rng.integers(
            low=100,
            high=1000,
            size=limit,
        )

        frequency = (
            timeframe_to_frequency(
                self.timeframe
            )
        )

        timestamps = pd.date_range(
            end=datetime.now(
                timezone.utc
            ),
            periods=limit,
            freq=frequency,
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

        self.market_data[pair] = data

        self.current_prices[pair] = float(
            close_prices[-1]
        )

    # --------------------------------------
    # MARKET UPDATE
    # --------------------------------------

    def update_market(
        self,
        pair,
    ):
        """
        Simulate one new market movement.

        Every call changes the current price
        and updates the latest candle.
        """

        self.initialize_pair(pair)

        current_price = (
            self.current_prices[pair]
        )

        volatility = (
            self.get_pair_volatility(pair)
        )

        trend = (
            self.get_pair_trend(pair)
        )

        # Random market movement
        random_return = self.rng.normal(
            loc=trend,
            scale=volatility,
        )

        # Calculate new price
        new_price = (
            current_price
            * np.exp(random_return)
        )

        # Prevent invalid prices
        new_price = max(
            new_price,
            0.00001
        )

        # Get the market history
        data = self.market_data[pair]

        # Update the latest candle
        last_index = data.index[-1]

        old_open = float(
            data.loc[
                last_index,
                "open"
            ]
        )

        old_high = float(
            data.loc[
                last_index,
                "high"
            ]
        )

        old_low = float(
            data.loc[
                last_index,
                "low"
            ]
        )

        # Update high
        new_high = max(
            old_high,
            new_price,
            old_open,
        )

        # Update low
        new_low = min(
            old_low,
            new_price,
            old_open,
        )

        # Update volume
        new_volume = int(
            data.loc[
                last_index,
                "volume"
            ]
            + self.rng.integers(
                10,
                100
            )
        )

        data.loc[
            last_index,
            "close"
        ] = new_price

        data.loc[
            last_index,
            "high"
        ] = new_high

        data.loc[
            last_index,
            "low"
        ] = new_low

        data.loc[
            last_index,
            "volume"
        ] = new_volume

        # Save new price
        self.current_prices[pair] = float(
            new_price
        )

        return float(
            new_price
        )

    # --------------------------------------
    # CREATE NEW CANDLE
    # --------------------------------------

    def add_new_candle(
        self,
        pair,
    ):
        """
        Close the current candle and create
        a new candle.

        Useful for making indicator data
        evolve during simulation.
        """

        self.initialize_pair(pair)

        data = self.market_data[pair]

        last_price = (
            self.current_prices[pair]
        )

        frequency = (
            timeframe_to_frequency(
                self.timeframe
            )
        )

        last_timestamp = (
            data["timestamp"].iloc[-1]
        )

        next_timestamp = (
            last_timestamp
            + pd.tseries.frequencies.to_offset(
                frequency
            )
        )

        new_row = pd.DataFrame({
            "timestamp": [
                next_timestamp
            ],
            "open": [
                last_price
            ],
            "high": [
                last_price
            ],
            "low": [
                last_price
            ],
            "close": [
                last_price
            ],
            "volume": [
                0
            ],
            "pair": [
                pair
            ],
        })

        self.market_data[pair] = pd.concat(
            [
                data,
                new_row,
            ],
            ignore_index=True,
        )

        # Keep history manageable
        maximum_history = 1000

        if (
            len(
                self.market_data[pair]
            )
            > maximum_history
        ):
            self.market_data[pair] = (
                self.market_data[pair]
                .iloc[-maximum_history:]
                .reset_index(drop=True)
            )

    # --------------------------------------
    # GET CANDLES
    # --------------------------------------

    def get_candles(
        self,
        pair,
        limit=250,
        update=True,
    ):
        """
        Return evolving OHLCV candles.

        By default, the market price moves
        every time this method is called.
        """

        self.initialize_pair(
            pair,
            limit=limit,
        )

        if update:

            # Simulate market movement
            self.update_market(pair)

        data = self.market_data[pair]

        return (
            data
            .tail(limit)
            .copy()
            .reset_index(drop=True)
        )

    # --------------------------------------
    # GET LATEST PRICE
    # --------------------------------------

    def get_latest_price(
        self,
        pair,
        update=True,
    ):
        """
        Return the latest simulated price.
        """

        self.initialize_pair(pair)

        if update:
            return self.update_market(pair)

        return float(
            self.current_prices[pair]
        )

    # --------------------------------------
    # UPDATE ALL PAIRS
    # --------------------------------------

    def update_all_pairs(
        self,
        pairs,
    ):
        """
        Update the market price for
        multiple Forex pairs.
        """

        self.update_count += 1

        prices = {}

        for pair in pairs:

            prices[pair] = (
                self.get_latest_price(
                    pair,
                    update=True,
                )
            )

        return prices

    # --------------------------------------
    # CREATE NEW CANDLES FOR ALL PAIRS
    # --------------------------------------

    def advance_market(
        self,
        pairs,
        movements=3,
    ):
        """
        Advance the simulated market.

        Parameters:
            pairs:
                Forex pairs to update.

            movements:
                Number of price movements
                before creating a new candle.

        This function makes the simulation
        behave more like a moving market.
        """

        self.update_count += 1

        prices = {}

        for pair in pairs:

            self.initialize_pair(pair)

            for _ in range(movements):

                price = (
                    self.update_market(
                        pair
                    )
                )

            # Occasionally create a new candle
            if (
                self.update_count % 2 == 0
            ):

                self.add_new_candle(
                    pair
                )

            prices[pair] = price

        return prices

    # --------------------------------------
    # MULTIPLE PAIRS
    # --------------------------------------

    def get_multiple_pairs(
        self,
        pairs,
        limit=250,
        update=True,
    ):
        """
        Get candle data for multiple pairs.
        """

        market_data = {}

        for pair in pairs:

            try:

                market_data[pair] = (
                    self.get_candles(
                        pair,
                        limit=limit,
                        update=update,
                    )
                )

            except Exception as error:

                print(
                    f"[DATA ERROR] "
                    f"Could not load "
                    f"{pair}: {error}"
                )

        return market_data


def create_data_feed():
    """
    Create and return a DataFeed instance.
    """

    return DataFeed()


if __name__ == "__main__":

    print(
        "Forex Paper Robot - "
        "Dynamic Data Feed Test"
    )

    print("-" * 50)

    feed = create_data_feed()

    test_pair = "EUR/USD"

    print(
        f"\nTesting evolving prices "
        f"for {test_pair}:\n"
    )

    # Show multiple changing prices
    for number in range(10):

        price = (
            feed.get_latest_price(
                test_pair,
                update=True,
            )
        )

        print(
            f"Update {number + 1}: "
            f"{price:.5f}"
        )

    print(
        "\nAdvancing the market..."
    )

    feed.advance_market(
        [test_pair],
        movements=5,
    )

    candles = (
        feed.get_candles(
            test_pair,
            limit=10,
            update=False,
        )
    )

    print(
        "\nLatest candles:"
    )

    print(candles)
