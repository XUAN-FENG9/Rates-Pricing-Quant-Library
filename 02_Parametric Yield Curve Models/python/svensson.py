import numpy as np


class SvenssonCurve:
    """
    Svensson model extends Nelson-Siegel
    with an additional curvature component.

    Used by:
    - central banks
    - sovereign curve modeling
    """

    def __init__(
        self,
        beta0,
        beta1,
        beta2,
        beta3,
        tau1,
        tau2
    ):

        self.beta0 = beta0
        self.beta1 = beta1
        self.beta2 = beta2
        self.beta3 = beta3
        self.tau1 = tau1
        self.tau2 = tau2

    def zero_rate(self, t):

        x1 = t / self.tau1
        x2 = t / self.tau2

        factor1 = (1 - np.exp(-x1)) / x1

        factor2 = factor1 - np.exp(-x1)

        factor3 = (
            (1 - np.exp(-x2)) / x2
            - np.exp(-x2)
        )

        return (
            self.beta0
            + self.beta1 * factor1
            + self.beta2 * factor2
            + self.beta3 * factor3
        )