"""
Interest-rate trade definitions for exposure and XVA analysis.

This module contains simple trade and netting-set classes.
The implementation is intentionally transparent and avoids
complex product abstractions.
"""

import numpy as np


class InterestRateSwap:
    """
    Plain-vanilla fixed-for-floating interest-rate swap.

    The swap is valued from the perspective of the party
    specified by pay_fixed.

    If pay_fixed is True:

        value = floating leg - fixed leg

    If pay_fixed is False:

        value = fixed leg - floating leg
    """

    def __init__(
        self,
        trade_id,
        notional,
        fixed_rate,
        start_time,
        end_time,
        pay_fixed=True
    ):
        self.trade_id = str(
            trade_id
        )

        self.notional = float(
            notional
        )

        self.fixed_rate = float(
            fixed_rate
        )

        self.start_time = float(
            start_time
        )

        self.end_time = float(
            end_time
        )

        self.pay_fixed = bool(
            pay_fixed
        )

        self.validate()

    def validate(
        self
    ):
        """
        Validate the trade definition.
        """

        if self.notional <= 0.0:
            raise ValueError(
                "Swap notional must be positive."
            )

        if not np.isfinite(
            self.fixed_rate
        ):
            raise ValueError(
                "Fixed rate must be finite."
            )

        if self.start_time < 0.0:
            raise ValueError(
                "Swap start time cannot be negative."
            )

        if self.end_time <= self.start_time:
            raise ValueError(
                "Swap end time must be after start time."
            )

    def direction(
        self
    ):
        """
        Return +1 for payer-fixed and -1 for receiver-fixed.
        """

        if self.pay_fixed:
            return 1.0

        return -1.0

    def summary(
        self
    ):
        """
        Return a dictionary containing the trade definition.
        """

        return {
            "trade_id": self.trade_id,
            "notional": self.notional,
            "fixed_rate": self.fixed_rate,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "pay_fixed": self.pay_fixed
        }


class NettingSet:
    """
    Collection of trades subject to close-out netting.

    Exposure is calculated from the portfolio value after
    summing all trade values within the netting set.
    """

    def __init__(
        self,
        netting_set_id,
        trades=None
    ):
        self.netting_set_id = str(
            netting_set_id
        )

        if trades is None:
            trades = []

        self.trades = list(
            trades
        )

        self.validate()

    def validate(
        self
    ):
        """
        Validate all trades in the netting set.
        """

        for trade in self.trades:
            if not isinstance(
                trade,
                InterestRateSwap
            ):
                raise TypeError(
                    "All trades must be InterestRateSwap objects."
                )

    def add_trade(
        self,
        trade
    ):
        """
        Add one trade to the netting set.
        """

        if not isinstance(
            trade,
            InterestRateSwap
        ):
            raise TypeError(
                "trade must be an InterestRateSwap."
            )

        self.trades.append(
            trade
        )

    def number_of_trades(
        self
    ):
        """
        Return the number of trades.
        """

        return len(
            self.trades
        )

    def maturity(
        self
    ):
        """
        Return the latest maturity in the netting set.
        """

        if not self.trades:
            return 0.0

        return max(
            trade.end_time
            for trade in self.trades
        )

    def summary(
        self
    ):
        """
        Return a simple summary dictionary.
        """

        return {
            "netting_set_id": self.netting_set_id,
            "number_of_trades": self.number_of_trades(),
            "maturity": self.maturity()
        }