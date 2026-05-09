class FRA:
    """
    Forward Rate Agreement (FRA)

    FRA allows counterparties to lock
    a future interest rate.

    Typical notation:
    -----------------
    3x6 FRA:
    - starts in 3 months
    - ends in 6 months

    Payoff
    ------
    Notional * (L - K) * accrual
    """

    def __init__(
        self,
        notional,
        strike,
        start,
        end
    ):

        self.notional = notional
        self.strike = strike
        self.start = start
        self.end = end

    def implied_forward_rate(self, curve):
        """
        Compute implied forward from curve.
        """

        return curve.forward_rate(
            self.start,
            self.end
        )

    def value(self, curve):
        """
        FRA present value.

        PV =
        N * (F-K) * accrual * DF
        """

        fwd = self.implied_forward_rate(curve)

        accrual = self.end - self.start

        df = curve.discount_factor(self.end)

        pv = (
            self.notional
            * (fwd - self.strike)
            * accrual
            * df
        )

        return pv