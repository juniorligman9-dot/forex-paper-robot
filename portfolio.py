"""
Portfolio management for the Forex Paper Trading Robot.

Tracks:
- Account balance
- Open trades
- Closed trades
- Realized profit/loss
- Unrealized profit/loss
- Daily trade count
"""

from datetime import datetime, timezone

from config import STARTING_BALANCE, ACCOUNT_CURRENCY


class Portfolio:
    """
    Manages the simulated paper-trading account.
    """

    def __init__(
        self,
        starting_balance=STARTING_BALANCE,
        account_currency=ACCOUNT_CURRENCY,
    ):
        if starting_balance <= 0:
            raise ValueError(
                "Starting balance must be greater than zero."
            )

        self.starting_balance = float(
            starting_balance
        )

        self.balance = float(
            starting_balance
        )

        self.account_currency = (
            account_currency
        )

        self.open_trades = []

        self.closed_trades = []

        self.trade_id_counter = 1

    def create_trade(
        self,
        pair,
        side,
        entry_price,
        position_size,
        stop_loss,
        take_profit,
    ):
        """
        Create and store a new open trade.
        """

        if side not in ["BUY", "SELL"]:
            raise ValueError(
                "Trade side must be BUY or SELL."
            )

        if entry_price <= 0:
            raise ValueError(
                "Entry price must be greater than zero."
            )

        if position_size <= 0:
            raise ValueError(
                "Position size must be greater than zero."
            )

        trade = {
            "id": self.trade_id_counter,
            "pair": pair,
            "side": side,
            "entry_price": float(entry_price),
            "position_size": float(position_size),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "opened_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "OPEN",
        }

        self.open_trades.append(
            trade
        )

        self.trade_id_counter += 1

        return trade.copy()

    def get_open_trade_by_pair(
        self,
        pair,
    ):
        """
        Return an open trade for a pair.

        Returns None if no open trade exists.
        """

        for trade in self.open_trades:
            if trade["pair"] == pair:
                return trade

        return None

    def calculate_trade_pnl(
        self,
        trade,
        current_price,
    ):
        """
        Calculate simplified paper-trading profit/loss.

        BUY:
            (current price - entry price) * position size

        SELL:
            (entry price - current price) * position size

        Note:
            This is a simplified calculation for paper
            trading and does not include broker-specific
            pip values, swaps, commissions, or currency
            conversion.
        """

        if current_price <= 0:
            raise ValueError(
                "Current price must be greater than zero."
            )

        entry_price = trade[
            "entry_price"
        ]

        position_size = trade[
            "position_size"
        ]

        if trade["side"] == "BUY":

            pnl = (
                current_price
                - entry_price
            ) * position_size

        elif trade["side"] == "SELL":

            pnl = (
                entry_price
                - current_price
            ) * position_size

        else:
            raise ValueError(
                "Invalid trade side."
            )

        return round(
            pnl,
            2
        )

    def close_trade(
        self,
        trade_id,
        exit_price,
        reason="MANUAL",
    ):
        """
        Close an open trade and update the balance.
        """

        if exit_price <= 0:
            raise ValueError(
                "Exit price must be greater than zero."
            )

        trade_to_close = None

        for trade in self.open_trades:
            if trade["id"] == trade_id:
                trade_to_close = trade
                break

        if trade_to_close is None:
            raise ValueError(
                f"Open trade {trade_id} was not found."
            )

        pnl = self.calculate_trade_pnl(
            trade_to_close,
            exit_price,
        )

        self.balance += pnl

        closed_trade = (
            trade_to_close.copy()
        )

        closed_trade["exit_price"] = float(
            exit_price
        )

        closed_trade["closed_at"] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        closed_trade["pnl"] = pnl

        closed_trade["close_reason"] = reason

        closed_trade["status"] = "CLOSED"

        self.open_trades.remove(
            trade_to_close
        )

        self.closed_trades.append(
            closed_trade
        )

        return closed_trade.copy()

    def get_unrealized_pnl(
        self,
        prices,
    ):
        """
        Calculate total unrealized profit/loss.

        Parameters:
            prices (dict)

        Example:
            {
                "EUR/USD": 1.0850,
                "GBP/USD": 1.2700
            }
        """

        total_pnl = 0.0

        for trade in self.open_trades:

            pair = trade["pair"]

            if pair not in prices:
                continue

            current_price = prices[
                pair
            ]

            pnl = (
                self.calculate_trade_pnl(
                    trade,
                    current_price,
                )
            )

            total_pnl += pnl

        return round(
            total_pnl,
            2
        )

    def get_equity(
        self,
        prices=None,
    ):
        """
        Return account equity.

        Equity =
            Balance + Unrealized P/L
        """

        if prices is None:
            prices = {}

        unrealized_pnl = (
            self.get_unrealized_pnl(
                prices
            )
        )

        equity = (
            self.balance
            + unrealized_pnl
        )

        return round(
            equity,
            2
        )

    def get_trades_today(
        self,
    ):
        """
        Count trades opened today using UTC time.
        """

        today = datetime.now(
            timezone.utc
        ).date()

        count = 0

        all_trades = (
            self.open_trades
            + self.closed_trades
        )

        for trade in all_trades:

            opened_at = (
                datetime.fromisoformat(
                    trade["opened_at"]
                )
            )

            if opened_at.date() == today:
                count += 1

        return count

    def get_summary(
        self,
        prices=None,
    ):
        """
        Return a summary of the paper account.
        """

        if prices is None:
            prices = {}

        unrealized_pnl = (
            self.get_unrealized_pnl(
                prices
            )
        )

        realized_pnl = (
            self.balance
            - self.starting_balance
        )

        total_pnl = (
            realized_pnl
            + unrealized_pnl
        )

        equity = (
            self.balance
            + unrealized_pnl
        )

        winning_trades = len([
            trade
            for trade in self.closed_trades
            if trade["pnl"] > 0
        ])

        losing_trades = len([
            trade
            for trade in self.closed_trades
            if trade["pnl"] < 0
        ])

        return {
            "starting_balance": round(
                self.starting_balance,
                2
            ),
            "balance": round(
                self.balance,
                2
            ),
            "equity": round(
                equity,
                2
            ),
            "realized_pnl": round(
                realized_pnl,
                2
            ),
            "unrealized_pnl": round(
                unrealized_pnl,
                2
            ),
            "total_pnl": round(
                total_pnl,
                2
            ),
            "open_trades": len(
                self.open_trades
            ),
            "closed_trades": len(
                self.closed_trades
            ),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "trades_today": self.get_trades_today(),
            "currency": self.account_currency,
        }


def create_portfolio():
    """
    Create and return a Portfolio instance.
    """

    return Portfolio()


if __name__ == "__main__":

    print(
        "Forex Paper Robot - Portfolio Test"
    )

    print("-" * 40)

    portfolio = create_portfolio()

    print(
        f"Starting Balance: "
        f"${portfolio.balance:.2f}"
    )

    # Create a test BUY trade
    trade = portfolio.create_trade(
        pair="EUR/USD",
        side="BUY",
        entry_price=1.0800,
        position_size=10000,
        stop_loss=1.0692,
        take_profit=1.1016,
    )

    print("\nTrade opened:")
    print(trade)

    # Simulate a new price
    current_prices = {
        "EUR/USD": 1.0850
    }

    print(
        "\nUnrealized P/L: "
        f"${portfolio.get_unrealized_pnl(current_prices):.2f}"
    )

    # Close the test trade
    closed_trade = portfolio.close_trade(
        trade_id=trade["id"],
        exit_price=1.0850,
        reason="TEST",
    )

    print("\nTrade closed:")
    print(closed_trade)

    print("\nPortfolio Summary:")

    summary = portfolio.get_summary()

    for key, value in summary.items():
        print(f"{key}: {value}")
