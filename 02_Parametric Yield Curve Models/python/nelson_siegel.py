import numpy as np


class NelsonSiegelCurve:
    """
    Nelson-Siegel parametric yield curve model.

    Model Formula
    --------------
    y(t) =
        beta0
        + beta1 * ((1 - exp(-t/tau)) / (t/tau))
        + beta2 * (((1 - exp(-t/tau)) / (t/tau)) - exp(-t/tau))

    Parameters
    ----------
    beta0 : long-term level
    beta1 : short-term slope
    beta2 : medium-term curvature
    tau   : decay parameter

    FO Interpretation
    -----------------
    beta0 → long-run rate level
    beta1 → steepness
    beta2 → hump/curvature
    tau   → location of hump
    """

    def __init__(self, beta0, beta1, beta2, tau):

        self.beta0 = beta0
        self.beta1 = beta1
        self.beta2 = beta2
        self.tau = tau

    def zero_rate(self, t):
        """
        Compute zero rate at maturity t.
        """

        x = t / self.tau

        factor1 = (1 - np.exp(-x)) / x

        factor2 = factor1 - np.exp(-x)

        return (
            self.beta0
            + self.beta1 * factor1
            + self.beta2 * factor2
        )

    def discount_factor(self, t):
        """
        Convert zero rate into discount factor.
        """

        r = self.zero_rate(t)

        return np.exp(-r * t)

    def forward_rate(self, t1, t2):
        """
        Implied forward rate.
        """

        df1 = self.discount_factor(t1)
        df2 = self.discount_factor(t2)

        return (df1 / df2 - 1) / (t2 - t1)