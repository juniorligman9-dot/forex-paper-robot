"""
Risk management for the Forex Paper Trading Robot.

This module controls:
- Risk per trade
- Position sizing
- Maximum open trades
- Maximum trades per day
- Stop loss
- Take profit
"""

from datetime import datetime, timezone

from config import (
    RISK_PER_TRADE_PERCENT,
    MAX_OPEN_TRADES,
    MAX_TRADES_PER_DAY,
    STOP_LOSS_PERCENT,
    TAKE_PROFIT_PERCENT,
)


class RiskManager:
    """
    Controls trading risk for the paper trading robot.
    """

    def __init__(
        self,
        risk_per_trade_percent=RISK_PER_TRADE_PERCENT,
        max_open_trades=MAX_OPEN_TRADES,
        max_trades_per_day=MAX_TRADES_PER_DAY,
        stop_loss_percent=STOP_LOSS_PERCENT,
        take_profit_percent=TAKE_PROFIT_PERCENT,
    ):
        self.risk_per_trade_percent = risk_per_trade_percent
        self.max_open_trades = max_open_trades
        self.max_trades_per_day = max_trades_per_day
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent

    def calculate_risk_amount(self, balance):
        """
        Calculate the maximum amount of money that can
        be risked on one trade.
        """

        if balance <= 0:
            return 0.0

        risk_amount = (
            balance
            * self.risk_per_trade_percent
            / 100
        )

        return round(risk_amount, 2)

    def calculate_stop_loss(
        self,
        entry_price,
        side,
    ):
        """
        Calculate the stop loss price.

        BUY:
            Stop loss below entry price.

        SELL:
            Stop loss above entry price.
        """

        if entry_price <= 0:
            raise ValueError(
                "Entry price must be greater than zero."
            )

        stop_distance = (
            entry_price
            * self.stop_loss_percent
            / 100
        )

        if side == "BUY":
            stop_loss = (
                entry_price - stop_distance
            )

        elif side == "SELL":
            stop_loss = (
                entry_price + stop_distance
            )

        else:
            raise ValueError(
                "Side must be BUY or SELL."
            )

        return stop_loss

    def calculate_take_profit(
        self,
        entry_price,
        side,
    ):
        """
        Calculate the take profit price.

        BUY:
            Take profit above entry price.

        SELL:
            Take profit below entry price.
        """

        if entry_price <= 0:
            raise ValueError(
                "Entry price must be greater than zero."
            )

        profit_distance = (
            entry_price
            * self.take_profit_percent
            / 100
        )

        if side == "BUY":
            take_profit = (
                entry_price + profit_distance
            )

        elif side == "SELL":
            take_profit = (
                entry_price - profit_distance
            )

        else:
            raise ValueError(
                "Side must be BUY or SELL."
            )

        return take_profit

    def calculate_position_size(
        self,
        balance,
        entry_price,
        stop_loss,
    ):
        """
        Calculate a simplified position size.

        Position size represents the number of price units
        for the paper-trading simulation.

        This is intentionally simplified. Real Forex position
        sizing requires broker-specific contract sizes, pip
        values, quote currencies, leverage, and margin rules.
        """

        if balance <= 0:
            return 0.0

        if entry_price <= 0:
            raise ValueError(
                "Entry price must be greater than zero."
            )

        risk_amount = (
            self.calculate_risk_amount(balance)
        )

        stop_distance = abs(
            entry_price - stop_loss
        )

        if stop_distance <= 0:
            return 0.0

        position_size = (
            risk_amount / stop_distance
        )

        return round(
            position_size,
            2
        )

    def can_open_trade(
        self,
        balance,
        open_trades,
        trades_today,
    ):
        """
        Check whether a new trade is allowed.

        Returns:
            tuple:
                (allowed, reason)
        """

        if balance <= 0:
            return (
                False,
                "Account balance is zero or below.",
            )

        if open_trades >= self.max_open_trades:
            return (
                False,
                (
                    "Maximum number of open trades "
                    "has been reached."
                ),
            )

        if trades_today >= self.max_trades_per_day:
            return (
                False,
                (
                    "Maximum number of daily trades "
                    "has been reached."
                ),
            )

        return (
            True,
            "Trade allowed.",
        )

    def create_trade_levels(
        self,
        balance,
        entry_price,
        side,
    ):
        """
        Create risk-managed trade levels.

        Returns:
            dict containing:
                risk_amount
                position_size
                stop_loss
                take_profit
        """

        stop_loss = (
            self.calculate_stop_loss(
                entry_price,
                side,
            )
        )

        take_profit = (
            self.calculate_take_profit(
                entry_price,
                side,
            )
        )

        position_size = (
            self.calculate_position_size(
                balance,
                entry_price,
                stop_loss,
            )
        )

        risk_amount = (
            self.calculate_risk_amount(
                balance
            )
        )

        return {
            "risk_amount": risk_amount,
            "position_size": position_size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
        }

    @staticmethod
    def get_current_day():
        """
        Return the current UTC trading day.
        """

        return datetime.now(
            timezone.utc
        ).date()


def create_risk_manager():
    """
    Create and return a RiskManager instance.
    """

    return RiskManager()


if __name__ == "__main__":
    print("Forex Paper Robot - Risk Manager Test")
    print("-" * 40)

    risk_manager = create_risk_manager()

    test_balance = 10000.00
    test_price = 1.08000
    test_side = "BUY"

    levels = (
        risk_manager.create_trade_levels(
            balance=test_balance,
            entry_price=test_price,
            side=test_side,
        )
    )

    print(f"Balance: ${test_balance:.2f}")
    print(f"Side: {test_side}")
    print(f"Entry Price: {test_price:.5f}")
    print(
        f"Risk Amount: "
        f"${levels['risk_amount']:.2f}"
    )
    print(
        f"Position Size: "
        f"{levels['position_size']:.2f}"
    )
    print(
        f"Stop Loss: "
        f"{levels['stop_loss']:.5f}"
    )
    print(
        f"Take Profit: "
        f"{levels['take_profit']:.5f}"
    )

    allowed, reason = (
        risk_manager.can_open_trade(
            balance=test_balance,
            open_trades=0,
            trades_today=0,
        )
    )

    print(f"Trade Allowed: {allowed}")
    print(f"Reason: {reason}")
