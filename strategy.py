"""
Trading strategy for the Forex Paper Trading Robot.

Uses:
- Fast EMA
- Slow EMA
- RSI

Signals:
- BUY
- SELL
- HOLD
"""

import pandas as pd

from config import (
    FAST_EMA_PERIOD,
    SLOW_EMA_PERIOD,
    RSI_PERIOD,
    RSI_BUY_LEVEL,
    RSI_SELL_LEVEL,
)

from indicators import add_indicators


BUY = "BUY"
SELL = "SELL"
HOLD = "HOLD"


class ForexStrategy:
    """
    EMA and RSI Forex trading strategy.
    """

    def __init__(
        self,
        fast_ema_period=FAST_EMA_PERIOD,
        slow_ema_period=SLOW_EMA_PERIOD,
        rsi_period=RSI_PERIOD,
        rsi_buy_level=RSI_BUY_LEVEL,
        rsi_sell_level=RSI_SELL_LEVEL,
    ):
        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period
        self.rsi_period = rsi_period
        self.rsi_buy_level = rsi_buy_level
        self.rsi_sell_level = rsi_sell_level

    def analyze(self, data):
        """
        Analyze market data and return a trading signal.

        Parameters:
            data (pandas.DataFrame): OHLCV candle data

        Returns:
            dict containing:
                signal
                price
                fast_ema
                slow_ema
                rsi
                reason
        """

        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "Strategy data must be a pandas DataFrame."
            )

        if data.empty:
            raise ValueError(
                "Strategy cannot analyze an empty DataFrame."
            )

        minimum_candles = max(
            self.slow_ema_period,
            self.rsi_period
        ) + 5

        if len(data) < minimum_candles:
            raise ValueError(
                f"Not enough candles. "
                f"Need at least {minimum_candles}."
            )

        # Calculate indicators
        analyzed_data = add_indicators(
            data,
            fast_ema_period=self.fast_ema_period,
            slow_ema_period=self.slow_ema_period,
            rsi_period=self.rsi_period,
        )

        # Get the latest completed candle
        latest = analyzed_data.iloc[-1]

        price = float(latest["close"])
        fast_ema = float(latest["ema_fast"])
        slow_ema = float(latest["ema_slow"])
        rsi = float(latest["rsi"])

        # Check for invalid indicator values
        if pd.isna(rsi):
            return self._build_result(
                HOLD,
                price,
                fast_ema,
                slow_ema,
                rsi,
                "RSI is not ready yet.",
            )

        # =========================
        # BUY CONDITIONS
        # =========================

        # Uptrend + positive momentum
        if (
            fast_ema > slow_ema
            and rsi >= self.rsi_buy_level
            and rsi < 70
        ):
            return self._build_result(
                BUY,
                price,
                fast_ema,
                slow_ema,
                rsi,
                (
                    "BUY: Fast EMA is above Slow EMA "
                    "and RSI confirms bullish momentum."
                ),
            )

        # =========================
        # SELL CONDITIONS
        # =========================

        # Downtrend + negative momentum
        if (
            fast_ema < slow_ema
            and rsi <= self.rsi_sell_level
            and rsi > 30
        ):
            return self._build_result(
                SELL,
                price,
                fast_ema,
                slow_ema,
                rsi,
                (
                    "SELL: Fast EMA is below Slow EMA "
                    "and RSI confirms bearish momentum."
                ),
            )

        # =========================
        # HOLD CONDITIONS
        # =========================

        return self._build_result(
            HOLD,
            price,
            fast_ema,
            slow_ema,
            rsi,
            (
                "HOLD: No valid EMA and RSI "
                "combination was found."
            ),
        )

    def _build_result(
        self,
        signal,
        price,
        fast_ema,
        slow_ema,
        rsi,
        reason,
    ):
        """
        Build a consistent strategy result.
        """

        return {
            "signal": signal,
            "price": price,
            "fast_ema": fast_ema,
            "slow_ema": slow_ema,
            "rsi": rsi,
            "reason": reason,
        }

    def get_signal(self, data):
        """
        Return only the BUY, SELL, or HOLD signal.
        """

        result = self.analyze(data)

        return result["signal"]


def create_strategy():
    """
    Create and return a ForexStrategy instance.
    """

    return ForexStrategy()


if __name__ == "__main__":
    from data_feed import create_data_feed

    print("Forex Paper Robot - Strategy Test")
    print("-" * 40)

    data_feed = create_data_feed()
    strategy = create_strategy()

    test_pair = "EUR/USD"

    candles = data_feed.get_candles(
        test_pair,
        limit=250,
    )

    result = strategy.analyze(candles)

    print(f"Pair: {test_pair}")
    print(f"Signal: {result['signal']}")
    print(f"Price: {result['price']:.5f}")
    print(f"Fast EMA: {result['fast_ema']:.5f}")
    print(f"Slow EMA: {result['slow_ema']:.5f}")
    print(f"RSI: {result['rsi']:.2f}")
    print(f"Reason: {result['reason']}")
