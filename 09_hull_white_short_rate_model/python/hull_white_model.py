"""
hull_white_model.py

One-factor Hull-White short-rate model.

Model:
------
dr(t) = [theta(t) - a r(t)] dt + sigma dW(t)

where:

- a     = mean reversion speed
- sigma = short-rate volatility
- theta(t) is chosen to fit the initial term structure

This chapter focuses on:
- curve-consistent short-rate dynamics
- discount bond pricing
- simulation
- bond option pricing
"""

import numpy as np


class HullWhiteModel:
    """
    One-factor Hull-White model.

    Parameters
    ----------
    mean_reversion : float
        Mean reversion speed a.

    volatility : float
        Short-rate volatility sigma.

    curve : YieldCurve
        Initial discount curve.
    """

    def __init__(
        self,
        mean_reversion,
        volatility,
        curve
    ):

        self.a = mean_reversion
        self.sigma = volatility
        self.curve = curve

    def B(self, t, T):
        """
        Hull-White B(t,T) function.

        B(t,T) measures sensitivity of the zero-coupon bond price
        to the short rate r(t).

        Formula:

            B(t,T) = (1 - exp(-a(T-t))) / a

        Parameters
        ----------
        t : float
            Current time.

        T : float
            Bond maturity.

        Returns
        -------
        float
            B(t,T).
        """

        if T < t:
            raise ValueError("Bond maturity T must be greater than or equal to t.")

        if abs(self.a) < 1e-12:
            return T - t

        return (
            1.0
            -
            np.exp(
                -self.a * (T - t)
            )
        ) / self.a

    def instantaneous_forward_rate(self, t, bump=1e-2):
        """
        Approximate instantaneous forward rate from the initial curve.

        The instantaneous forward rate is:

            f(0,t) = - d log P(0,t) / dt

        We compute it numerically using central differences.

        Parameters
        ----------
        t : float
            Time.

        bump : float
            Finite difference bump.

        Returns
        -------
        float
            Instantaneous forward rate.
        """

        t1 = max(t - bump, 1e-6)
        t2 = t + bump

        p1 = self.curve.discount_factor(t1)
        p2 = self.curve.discount_factor(t2)

        return -(
            np.log(p2)
            -
            np.log(p1)
        ) / (t2 - t1)

    def instantaneous_forward_derivative(self, t, bump=5e-2):
        """
        Numerical derivative of the instantaneous forward rate.

        This is used in the theoretical theta(t) expression.

        Parameters
        ----------
        t : float
            Time.

        bump : float
            Finite difference bump.

        Returns
        -------
        float
            df(0,t) / dt.
        """

        t1 = max(t - bump, 1e-6)
        t2 = t + bump

        f1 = self.instantaneous_forward_rate(t1)
        f2 = self.instantaneous_forward_rate(t2)

        return (f2 - f1) / (t2 - t1)

    def theta(self, t):
        """
        Hull-White drift function theta(t).

        For the model:

            dr = [theta(t) - a r] dt + sigma dW

        theta(t) is chosen so that the model fits the initial discount curve.

        A commonly used expression is:

            theta(t)
            =
            df(0,t)/dt
            + a f(0,t)
            + sigma^2/(2a) * (1 - exp(-2at))

        Returns
        -------
        float
            Drift adjustment theta(t).
        """

        f = self.instantaneous_forward_rate(t)

        dfdt = self.instantaneous_forward_derivative(t)

        if abs(self.a) < 1e-12:
            convexity = self.sigma * self.sigma * t
        else:
            convexity = (
                self.sigma
                *
                self.sigma
                /
                (2.0 * self.a)
                *
                (
                    1.0
                    -
                    np.exp(
                        -2.0 * self.a * t
                    )
                )
            )

        return (
            dfdt
            +
            self.a * f
            +
            convexity
        )

    def short_rate_drift(self, t, r):
        """
        Drift of the short rate process.

        Parameters
        ----------
        t : float
            Time.

        r : float
            Current short rate.

        Returns
        -------
        float
            Drift term.
        """

        return self.theta(t) - self.a * r

    def evolve_short_rate(
        self,
        t,
        r,
        dt,
        z
    ):
        """
        One Euler step for the Hull-White short-rate process.

        Parameters
        ----------
        t : float
            Current time.

        r : float
            Current short rate.

        dt : float
            Time step.

        z : float
            Standard normal random variable.

        Returns
        -------
        float
            Next short rate.
        """

        drift = self.short_rate_drift(
            t,
            r
        )

        return (
            r
            +
            drift * dt
            +
            self.sigma
            *
            np.sqrt(dt)
            *
            z
        )