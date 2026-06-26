"""
stochastic_vol_model.py

Chapter 10 — Short Rate Models with Stochastic Volatility.

This model extends the Chapter 09 Hull-White model:

    dr_t = [theta(t) - a r_t] dt + sigma dW_t

to a stochastic-volatility version:

    dr_t = [theta(t) - a r_t] dt + sqrt(v_t) dW_t^r

    dv_t = kappa (v_bar - v_t) dt + eta sqrt(v_t) dW_t^v

with:

    corr(dW_t^r, dW_t^v) = rho dt

The model reuses the Chapter 09 HullWhiteModel object for:
- theta(t)
- mean reversion a
- initial curve
"""

import numpy as np


class StochasticVolShortRateModel:
    """
    Hull-White-style short-rate model with stochastic variance.

    Parameters
    ----------
    base_hw_model : HullWhiteModel
        Chapter 09 Hull-White model. We reuse theta(t), curve and a.

    kappa : float
        Variance mean reversion speed.

    v_bar : float
        Long-run variance level.

    eta : float
        Volatility of variance.

    rho : float
        Correlation between short-rate shock and variance shock.
    """

    def __init__(
        self,
        base_hw_model,
        kappa,
        v_bar,
        eta,
        rho
    ):
        self.base_hw_model = base_hw_model
        self.a = base_hw_model.a
        self.curve = base_hw_model.curve

        self.kappa = kappa
        self.v_bar = v_bar
        self.eta = eta
        self.rho = rho

        if self.kappa <= 0:
            raise ValueError("kappa must be positive.")

        if self.v_bar <= 0:
            raise ValueError("v_bar must be positive.")

        if self.eta < 0:
            raise ValueError("eta must be non-negative.")

        if self.rho <= -1.0 or self.rho >= 1.0:
            raise ValueError("rho must be between -1 and 1.")

    def theta(self, t):
        """
        Reuse Hull-White theta(t) from Chapter 09.
        """

        return self.base_hw_model.theta(t)

    def short_rate_drift(self, t, r):
        """
        Short-rate drift:

            theta(t) - a r_t
        """

        return self.theta(t) - self.a * r

    def variance_drift(self, v):
        """
        CIR-style variance drift:

            kappa (v_bar - v_t)
        """

        return self.kappa * (self.v_bar - v)

    def evolve(
        self,
        t,
        r,
        v,
        dt,
        z_rate,
        z_vol
    ):
        """
        Evolve short rate and variance by one Euler step.

        Full truncation is used to keep variance non-negative.
        """

        v_pos = max(v, 0.0)

        r_next = (
            r
            +
            self.short_rate_drift(t, r) * dt
            +
            np.sqrt(v_pos) * np.sqrt(dt) * z_rate
        )

        v_next = (
            v
            +
            self.variance_drift(v_pos) * dt
            +
            self.eta * np.sqrt(v_pos) * np.sqrt(dt) * z_vol
        )

        v_next = max(v_next, 0.0)

        return r_next, v_next

    def instantaneous_volatility(self, v):
        """
        Convert variance into instantaneous short-rate volatility.
        """

        return np.sqrt(max(v, 0.0))