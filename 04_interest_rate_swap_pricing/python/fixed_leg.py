class FixedLeg:
    """
    Fixed leg of an interest rate swap.

    Fixed coupons are deterministic.

    Cashflow:
    ----------
    N * K * accrual
    """

    def __init__(
        self,
        notional,
        fixed_rate,
        payment_dates
    ):

        self.notional = notional
        self.fixed_rate = fixed_rate
        self.payment_dates = payment_dates

    def pv(self, curve):
        """
        Present value of fixed leg.
        """

        pv = 0.0

        previous = 0.0

        for t in self.payment_dates:

            accrual = t - previous

            cashflow = (
                self.notional
                * self.fixed_rate
                * accrual
            )

            df = curve.discount_factor(t)

            pv += cashflow * df

            previous = t

        return pv