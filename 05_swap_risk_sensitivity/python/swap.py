class InterestRateSwap:
    """
    Vanilla fixed-for-floating interest rate swap.
    """

    def __init__(
        self,
        notional,
        fixed_rate,
        maturity,
        payment_frequency=2,
        payer=True
    ):

        self.notional = notional

        self.fixed_rate = fixed_rate

        self.maturity = maturity

        self.payment_frequency = payment_frequency

        self.payer = payer

        self.payment_dates = []

        step = 1 / payment_frequency

        t = step

        while t <= maturity + 1e-10:

            self.payment_dates.append(
                round(t, 10)
            )

            t += step

    def fixed_leg_pv(self, curve):

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

    def floating_leg_pv(self, curve):

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

    def npv(self, curve):

        fixed_pv = self.fixed_leg_pv(curve)

        float_pv = self.floating_leg_pv(curve)

        if self.payer:

            return float_pv - fixed_pv

        else:

            return fixed_pv - float_pv