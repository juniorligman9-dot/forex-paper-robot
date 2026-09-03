"""
Paper broker for the Forex Paper Trading Robot.

This module simulates:
- Opening BUY and SELL trades
- Applying simulated spread
- Applying simulated slippage
- Checking Stop Loss
- Checking Take Profit
- Closing paper trades
"""

from config import (
    SIMULATED_SPREAD_PERCENT,
    SIMULATED_SLIPPAGE_PERCENT,
)

from portfolio import create_portfolio
from risk_manager import create_risk_manager


class PaperBroker:
    """
    Simulated Forex broker for paper trading.
    """

    def __init__(
        self,
        portfolio=None,
        risk_manager=None,
    ):
        self.portfolio = (
            portfolio
            if portfolio is not None
            else create_portfolio()
        )

        self.risk_manager = (
            risk_manager
            if risk_manager is not None
            else create_risk_manager()
        )

    def apply_entry_costs(
        self,
        price,
        side,
    ):
        """
        Apply simulated spread and slippage
        to an entry price.
        """

        if price <= 0:
            raise ValueError(
                "Price must be greater than zero."
            )

        spread_cost = (
            price
            * SIMULATED_SPREAD_PERCENT
            / 100
        )

        slippage_cost = (
            price
            * SIMULATED_SLIPPAGE_PERCENT
            / 100
        )

        total_cost = (
            spread_cost
            + slippage_cost
        )

        if side == "BUY":
            adjusted_price = (
                price + total_cost
            )

        elif side == "SELL":
            adjusted_price = (
                price - total_cost
            )

        else:
            raise ValueError(
                "Side must be BUY or SELL."
            )

        return adjusted_price

    def apply_exit_costs(
        self,
        price,
        side,
    ):
        """
        Apply simulated spread and slippage
        to an exit price.
        """

        if price <= 0:
            raise ValueError(
                "Price must be greater than zero."
            )

        spread_cost = (
            price
            * SIMULATED_SPREAD_PERCENT
            / 100
        )

        slippage_cost = (
            price
            * SIMULATED_SLIPPAGE_PERCENT
            / 100
        )

        total_cost = (
            spread_cost
            + slippage_cost
        )

        if side == "BUY":
            adjusted_price = (
                price - total_cost
            )

        elif side == "SELL":
            adjusted_price = (
                price + total_cost
            )

        else:
            raise ValueError(
                "Side must be BUY or SELL."
            )

        return adjusted_price

    def can_open_trade(
        self,
    ):
        """
        Check whether the account is allowed
        to open another trade.
        """

        open_trades = len(
            self.portfolio.open_trades
        )

        trades_today = (
            self.portfolio.get_trades_today()
        )

        return (
            self.risk_manager.can_open_trade(
                balance=self.portfolio.balance,
                open_trades=open_trades,
                trades_today=trades_today,
            )
        )

    def open_trade(
        self,
        pair,
        side,
        market_price,
    ):
        """
        Open a new paper trade.

        Parameters:
            pair (str): Forex pair
            side (str): BUY or SELL
            market_price (float): Current price

        Returns:
            dict
        """

        if side not in ["BUY", "SELL"]:
            return {
                "success": False,
                "reason": (
                    "Side must be BUY or SELL."
                ),
            }

        if market_price <= 0:
            return {
                "success": False,
                "reason": (
                    "Market price must be greater than zero."
                ),
            }

        # Prevent multiple trades on the same pair
        existing_trade = (
            self.portfolio.get_open_trade_by_pair(
                pair
            )
        )

        if existing_trade is not None:
            return {
                "success": False,
                "reason": (
                    f"There is already an open "
                    f"trade for {pair}."
                ),
            }

        # Check risk limits
        allowed, reason = (
            self.can_open_trade()
        )

        if not allowed:
            return {
                "success": False,
                "reason": reason,
            }

        # Apply simulated entry costs
        entry_price = (
            self.apply_entry_costs(
                market_price,
                side,
            )
        )

        # Calculate trade levels
        levels = (
            self.risk_manager.create_trade_levels(
                balance=self.portfolio.balance,
                entry_price=entry_price,
                side=side,
            )
        )

        position_size = (
            levels["position_size"]
        )

        if position_size <= 0:
            return {
                "success": False,
                "reason": (
                    "Calculated position size "
                    "is zero or invalid."
                ),
            }

        # Create the trade
        trade = (
            self.portfolio.create_trade(
                pair=pair,
                side=side,
                entry_price=entry_price,
                position_size=position_size,
                stop_loss=levels["stop_loss"],
                take_profit=levels["take_profit"],
            )
        )

        return {
            "success": True,
            "reason": "Paper trade opened.",
            "trade": trade,
            "risk": levels,
        }

    def close_trade(
        self,
        trade_id,
        market_price,
        reason="MANUAL",
    ):
        """
        Close a paper trade.
        """

        trade = None

        for open_trade in (
            self.portfolio.open_trades
        ):
            if open_trade["id"] == trade_id:
                trade = open_trade
                break

        if trade is None:
            return {
                "success": False,
                "reason": (
                    f"Open trade {trade_id} "
                    f"was not found."
                ),
            }

        exit_price = (
            self.apply_exit_costs(
                market_price,
                trade["side"],
            )
        )

        closed_trade = (
            self.portfolio.close_trade(
                trade_id=trade_id,
                exit_price=exit_price,
                reason=reason,
            )
        )

        return {
            "success": True,
            "reason": "Paper trade closed.",
            "trade": closed_trade,
        }

    def check_open_trades(
        self,
        prices,
    ):
        """
        Check all open trades for
        Stop Loss or Take Profit.

        Parameters:
            prices (dict)

        Example:
            {
                "EUR/USD": 1.0850,
                "GBP/USD": 1.2700
            }

        Returns:
            list of closed trade results
        """

        results = []

        # Create a copy because trades may be
        # removed while looping.
        open_trades = list(
            self.portfolio.open_trades
        )

        for trade in open_trades:

            pair = trade["pair"]

            if pair not in prices:
                continue

            market_price = prices[pair]

            side = trade["side"]
            stop_loss = trade["stop_loss"]
            take_profit = (
                trade["take_profit"]
            )

            close_reason = None

            # BUY trade checks
            if side == "BUY":

                if market_price <= stop_loss:
                    close_reason = "STOP_LOSS"

                elif market_price >= take_profit:
                    close_reason = "TAKE_PROFIT"

            # SELL trade checks
            elif side == "SELL":

                if market_price >= stop_loss:
                    close_reason = "STOP_LOSS"

                elif market_price <= take_profit:
                    close_reason = "TAKE_PROFIT"

            # Close if necessary
            if close_reason is not None:

                result = (
                    self.close_trade(
                        trade_id=trade["id"],
                        market_price=market_price,
                        reason=close_reason,
                    )
                )

                results.append(
                    result
                )

        return results

    def get_account_summary(
        self,
        prices=None,
    ):
        """
        Return the current paper account summary.
        """

        if prices is None:
            prices = {}

        return (
            self.portfolio.get_summary(
                prices
            )
        )


def create_paper_broker():
    """
    Create and return a PaperBroker instance.
    """

    return PaperBroker()


if __name__ == "__main__":

    print(
        "Forex Paper Robot - Paper Broker Test"
    )

    print("-" * 45)

    broker = create_paper_broker()

    test_pair = "EUR/USD"
    test_price = 1.0800

    # Open a test trade
    result = broker.open_trade(
        pair=test_pair,
        side="BUY",
        market_price=test_price,
    )

    print("\nOpen Trade Result:")
    print(result)

    # Check account summary
    prices = {
        test_pair: 1.0850
    }

    print("\nAccount Summary:")
    summary = (
        broker.get_account_summary(
            prices
        )
    )

    for key, value in summary.items():
        print(f"{key}: {value}")

    # Check Stop Loss / Take Profit
    closed_results = (
        broker.check_open_trades(
            prices
        )
    )

    if closed_results:
        print(
            "\nTrades Closed Automatically:"
        )

        for closed in closed_results:
            print(closed)
    else:
        print(
            "\nNo trades were closed."
        )
