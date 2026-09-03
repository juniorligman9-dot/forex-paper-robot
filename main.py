"""
Main application for the Forex Paper Trading Robot.

Workflow:
1. Advance the simulated Forex market once
2. Get a consistent price snapshot
3. Check existing trades for Stop Loss / Take Profit
4. Analyze all configured Forex pairs
5. Generate BUY, SELL, or HOLD signals
6. Open paper trades when allowed
7. Display account summary

This version uses simulated market data and
does NOT place real trades.
"""

import time
import traceback
from datetime import datetime, timezone

from config import (
    BOT_NAME,
    PAPER_TRADING,
    DEBUG,
    FOREX_PAIRS,
    CANDLE_LIMIT,
    SCAN_INTERVAL_SECONDS,
)

from data_feed import create_data_feed
from strategy import create_strategy, BUY, SELL, HOLD
from paper_broker import create_paper_broker


class ForexPaperRobot:
    """
    Main controller for the Forex Paper Trading Robot.
    """

    def __init__(self):
        self.data_feed = create_data_feed()
        self.strategy = create_strategy()
        self.broker = create_paper_broker()

        self.running = False
        self.scan_number = 0

        # Number of simulated price movements
        # per scan.
        self.market_movements_per_scan = 3

    def advance_market(self):
        """
        Advance the entire simulated market once.

        Returns:
            dict of current prices
        """

        return self.data_feed.advance_market(
            pairs=FOREX_PAIRS,
            movements=self.market_movements_per_scan,
        )

    def get_current_prices(self):
        """
        Get a price snapshot without causing
        additional market movement.
        """

        prices = {}

        for pair in FOREX_PAIRS:
            try:
                prices[pair] = (
                    self.data_feed.get_latest_price(
                        pair,
                        update=False,
                    )
                )

            except Exception as error:
                print(
                    f"[PRICE ERROR] "
                    f"{pair}: {error}"
                )

        return prices

    def analyze_pair(self, pair):
        """
        Analyze one Forex pair using the
        current market state.

        No additional market movement occurs
        during analysis.
        """

        try:
            candles = (
                self.data_feed.get_candles(
                    pair,
                    limit=CANDLE_LIMIT,
                    update=False,
                )
            )

            result = (
                self.strategy.analyze(
                    candles
                )
            )

            return result

        except Exception as error:
            print(
                f"[ANALYSIS ERROR] "
                f"{pair}: {error}"
            )

            if DEBUG:
                traceback.print_exc()

            return None

    def process_signal(
        self,
        pair,
        result,
    ):
        """
        Process a BUY, SELL, or HOLD signal.
        """

        if result is None:
            return

        signal = result["signal"]
        price = result["price"]

        # Ignore HOLD signals
        if signal == HOLD:
            return

        print(
            f"\n[SIGNAL] "
            f"{pair} | {signal}"
        )

        print(
            f"Price: {price:.5f} | "
            f"RSI: {result['rsi']:.2f}"
        )

        print(
            f"Fast EMA: "
            f"{result['fast_ema']:.5f} | "
            f"Slow EMA: "
            f"{result['slow_ema']:.5f}"
        )

        print(
            f"Reason: "
            f"{result['reason']}"
        )

        # Try to open a paper trade
        trade_result = (
            self.broker.open_trade(
                pair=pair,
                side=signal,
                market_price=price,
            )
        )

        if trade_result["success"]:

            trade = (
                trade_result["trade"]
            )

            risk = (
                trade_result["risk"]
            )

            print(
                f"[TRADE OPENED] "
                f"ID: {trade['id']}"
            )

            print(
                f"Pair: {trade['pair']}"
            )

            print(
                f"Side: {trade['side']}"
            )

            print(
                f"Entry: "
                f"{trade['entry_price']:.5f}"
            )

            print(
                f"Stop Loss: "
                f"{trade['stop_loss']:.5f}"
            )

            print(
                f"Take Profit: "
                f"{trade['take_profit']:.5f}"
            )

            print(
                f"Position Size: "
                f"{trade['position_size']:.2f}"
            )

            print(
                f"Risk Amount: "
                f"${risk['risk_amount']:.2f}"
            )

        else:

            print(
                f"[TRADE BLOCKED] "
                f"{trade_result['reason']}"
            )

    def check_open_trades(
        self,
        prices,
    ):
        """
        Check all open trades for Stop Loss
        and Take Profit conditions.
        """

        closed_results = (
            self.broker.check_open_trades(
                prices
            )
        )

        for result in closed_results:

            if not result["success"]:
                continue

            trade = result["trade"]

            print(
                f"\n[TRADE CLOSED] "
                f"ID: {trade['id']}"
            )

            print(
                f"Pair: {trade['pair']}"
            )

            print(
                f"Side: {trade['side']}"
            )

            print(
                f"Entry Price: "
                f"{trade['entry_price']:.5f}"
            )

            print(
                f"Exit Price: "
                f"{trade['exit_price']:.5f}"
            )

            print(
                f"P/L: "
                f"${trade['pnl']:.2f}"
            )

            print(
                f"Reason: "
                f"{trade['close_reason']}"
            )

    def print_signal_summary(
        self,
        buy_count,
        sell_count,
        hold_count,
    ):
        """
        Print the signal totals for the scan.
        """

        print("\n" + "-" * 40)
        print("SIGNAL SUMMARY")
        print("-" * 40)

        print(
            f"BUY signals:  {buy_count}"
        )

        print(
            f"SELL signals: {sell_count}"
        )

        print(
            f"HOLD signals: {hold_count}"
        )

    def print_summary(
        self,
        prices,
    ):
        """
        Print the current paper account summary.
        """

        summary = (
            self.broker.get_account_summary(
                prices
            )
        )

        print("\n" + "=" * 50)
        print("PAPER ACCOUNT SUMMARY")
        print("=" * 50)

        currency = summary["currency"]

        print(
            f"Starting Balance: "
            f"{currency} "
            f"{summary['starting_balance']:.2f}"
        )

        print(
            f"Balance: "
            f"{currency} "
            f"{summary['balance']:.2f}"
        )

        print(
            f"Equity: "
            f"{currency} "
            f"{summary['equity']:.2f}"
        )

        print(
            f"Realized P/L: "
            f"{currency} "
            f"{summary['realized_pnl']:.2f}"
        )

        print(
            f"Unrealized P/L: "
            f"{currency} "
            f"{summary['unrealized_pnl']:.2f}"
        )

        print(
            f"Total P/L: "
            f"{currency} "
            f"{summary['total_pnl']:.2f}"
        )

        print(
            f"Open Trades: "
            f"{summary['open_trades']}"
        )

        print(
            f"Closed Trades: "
            f"{summary['closed_trades']}"
        )

        print(
            f"Winning Trades: "
            f"{summary['winning_trades']}"
        )

        print(
            f"Losing Trades: "
            f"{summary['losing_trades']}"
        )

        print(
            f"Trades Today: "
            f"{summary['trades_today']}"
        )

        print("=" * 50)

    def run_scan(self):
        """
        Run one complete Forex market scan.

        The market is advanced only once at
        the beginning of the scan.
        """

        self.scan_number += 1

        scan_time = datetime.now(
            timezone.utc
        ).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        print("\n" + "=" * 60)
        print(
            f"SCAN #{self.scan_number}"
        )
        print(
            f"Time: {scan_time}"
        )
        print(
            f"Pairs to scan: "
            f"{len(FOREX_PAIRS)}"
        )
        print("=" * 60)

        # ----------------------------------
        # STEP 1
        # Advance the simulated market once
        # ----------------------------------

        self.advance_market()

        # ----------------------------------
        # STEP 2
        # Create a stable price snapshot
        # ----------------------------------

        prices = (
            self.get_current_prices()
        )

        # ----------------------------------
        # STEP 3
        # Check existing trades
        # ----------------------------------

        self.check_open_trades(
            prices
        )

        # ----------------------------------
        # STEP 4
        # Analyze all Forex pairs
        # ----------------------------------

        buy_count = 0
        sell_count = 0
        hold_count = 0

        for pair in FOREX_PAIRS:

            result = (
                self.analyze_pair(
                    pair
                )
            )

            if result is None:
                continue

            signal = result["signal"]

            if signal == BUY:
                buy_count += 1

            elif signal == SELL:
                sell_count += 1

            elif signal == HOLD:
                hold_count += 1

            # Process only BUY and SELL
            if signal in [BUY, SELL]:

                self.process_signal(
                    pair,
                    result,
                )

        # ----------------------------------
        # STEP 5
        # Get final stable price snapshot
        # ----------------------------------

        latest_prices = (
            self.get_current_prices()
        )

        # Print results
        self.print_signal_summary(
            buy_count,
            sell_count,
            hold_count,
        )

        self.print_summary(
            latest_prices
        )

    def start(self):
        """
        Start the continuous scanning loop.
        """

        if not PAPER_TRADING:
            raise RuntimeError(
                "This version is configured "
                "for paper trading only."
            )

        self.running = True

        print("\n" + "=" * 60)
        print(BOT_NAME)
        print("MODE: PAPER TRADING")
        print(
            "NO REAL MONEY IS BEING TRADED"
        )
        print("=" * 60)

        print(
            f"\nScanning "
            f"{len(FOREX_PAIRS)} "
            f"Forex pairs."
        )

        print(
            f"Market movements per scan: "
            f"{self.market_movements_per_scan}"
        )

        print(
            f"Scan interval: "
            f"{SCAN_INTERVAL_SECONDS} seconds"
        )

        print(
            "\nPress CTRL+C to stop "
            "the robot."
        )

        try:

            while self.running:

                self.run_scan()

                if not self.running:
                    break

                print(
                    f"\nWaiting "
                    f"{SCAN_INTERVAL_SECONDS} "
                    f"seconds..."
                )

                time.sleep(
                    SCAN_INTERVAL_SECONDS
                )

        except KeyboardInterrupt:

            print(
                "\n\nRobot stopped by user."
            )

            self.running = False

        except Exception as error:

            print(
                f"\n[FATAL ERROR] "
                f"{error}"
            )

            if DEBUG:
                traceback.print_exc()

            self.running = False

    def stop(self):
        """
        Stop the robot safely.
        """

        self.running = False


def main():
    """
    Application entry point.
    """

    robot = ForexPaperRobot()

    robot.start()


if __name__ == "__main__":
    main()
