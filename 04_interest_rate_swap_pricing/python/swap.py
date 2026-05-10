from fixed_leg import FixedLeg
from floating_leg import FloatingLeg


class InterestRateSwap:
    """
    Plain vanilla fixed-for-floating IRS.

    Payer swap:
    - pay fixed
    - receive floating

    Receiver swap:
    - receive fixed
    - pay floating
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

        step = 1 / payment_frequency

        self.payment_dates = []

        t = step

        while t <= maturity + 1e-10:

            self.payment_dates.append(round(t, 10))

            t += step

        self.fixed_leg = FixedLeg(
            notional,
            fixed_rate,
            self.payment_dates
        )

        self.floating_leg = FloatingLeg(
            notional,
            self.payment_dates
        )

    def npv(self, curve):
        """
        Swap NPV.

        Payer:
        float - fixed

        Receiver:
        fixed - float
        """

        fixed_pv = self.fixed_leg.pv(curve)

        float_pv = self.floating_leg.pv(curve)

        if self.payer:

            return float_pv - fixed_pv

        else:

            return fixed_pv - float_pv

    def par_swap_rate(self, curve):
        """
        Compute par swap rate.

        Par rate makes swap NPV = 0.
        """

        numerator = (
            1 - curve.discount_factor(self.maturity)
        )

        denominator = 0.0

        previous = 0.0

        for t in self.payment_dates:

            accrual = t - previous

            denominator += (
                accrual
                * curve.discount_factor(t)
            )

            previous = t

        return numerator / denominator