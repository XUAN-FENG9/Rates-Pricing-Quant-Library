class FloatingLeg:
    """
    Floating leg of an IRS.

    Floating coupons depend on
    implied forward rates.
    """

    def __init__(
        self,
        notional,
        payment_dates
    ):

        self.notional = notional
        self.payment_dates = payment_dates

    def pv(self, curve):
        """
        Present value of floating leg.
        """

        pv = 0.0

        previous = 0.0

        for t in self.payment_dates:

            accrual = t - previous

            fwd = curve.forward_rate(
                previous,
                t
            )

            cashflow = (
                self.notional
                * fwd
                * accrual
            )

            df = curve.discount_factor(t)

            pv += cashflow * df

            previous = t

        return pv