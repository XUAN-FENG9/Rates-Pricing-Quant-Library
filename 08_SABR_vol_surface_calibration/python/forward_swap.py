import numpy as np


class ForwardStartingSwap:
    """
    Forward-starting interest rate swap.

    Example:
    ----------
    1Y x 5Y swap:

    start = 1Y
    end   = 6Y

    This is the correct underlying
    for a European swaption.
    """

    def __init__(
        self,
        notional,
        fixed_rate,
        start,
        end,
        payment_frequency=2
    ):

        self.notional = notional

        self.fixed_rate = fixed_rate

        self.start = start

        self.end = end

        self.payment_frequency = payment_frequency

        self.payment_dates = []

        step = 1 / payment_frequency

        t = start + step

        while t <= end + 1e-10:

            self.payment_dates.append(
                round(t, 10)
            )

            t += step

    def annuity(self, curve):
        """
        Forward swap annuity.

        A(0)
        =
        sum(delta_i * P(0,T_i))
        """

        annuity = 0.0

        previous = self.start

        for t in self.payment_dates:

            accrual = t - previous

            df = curve.discount_factor(t)

            annuity += accrual * df

            previous = t

        return annuity

    def forward_swap_rate(self, curve):
        """
        Proper forward swap rate:

        S(0;T0,Tn)
        """

        P0 = curve.discount_factor(
            self.start
        )

        Pn = curve.discount_factor(
            self.end
        )

        annuity = self.annuity(curve)

        return (P0 - Pn) / annuity