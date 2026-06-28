"""
hull_white_tree.py

Simple recombining binomial short-rate tree for Hull-White dynamics.

This is an educational tree implementation.

Production Hull-White Bermudan pricing usually uses a calibrated
trinomial tree or finite-difference method.

In this educational recombining binomial approximation to the Hull–White short-rate model:

The short rate at node (i,j) is approximated as

    r(i,j)=r0+(2j-i)dr

where

    i = time step

    j = node index

This symmetric construction provides a simple
binomial approximation.

Production Hull–White implementations typically
use calibrated recombining trinomial trees instead.
"""

import numpy as np


class HullWhiteBinomialTree:
    """
    Recombining binomial tree for the short rate.

    Node rate:

        r(i,j) = r0 + (2j - i) dr

    where:

        dr = sigma * sqrt(dt)
    """

    def __init__(
        self,
        model,
        maturity,
        n_steps,
        r0=None
    ):

        self.model = model
        self.maturity = maturity
        self.n_steps = n_steps

        self.dt = maturity / n_steps

        self.times = np.linspace(
            0.0,
            maturity,
            n_steps + 1
        )

        if r0 is None:

            self.r0 = model.instantaneous_forward_rate(
                1e-6
            )

        else:

            self.r0 = r0

        self.dr = (
            model.sigma
            *
            np.sqrt(self.dt)
        )

        self.rates = []
        self.probabilities = []

        self.build_tree()

    def node_rate(
        self,
        step,
        node
    ):
        """
        Short rate at node (step, node).
        """

        return (
            self.r0
            +
            (2 * node - step)
            *
            self.dr
        )

    def transition_probability(
        self,
        step,
        node
    ):
        """
        Risk-neutral up probability.

        Approximation:

            E[dr] = [theta(t) - a r] dt

        Binomial expected move:

            E[dr] = (2p - 1) dr

        Hence:

            p = 0.5 + drift * dt / (2 dr)
        """

        t = self.times[step]

        r = self.node_rate(
            step,
            node
        )

        drift = self.model.short_rate_drift(
            t,
            r
        )

        if abs(self.dr) < 1e-12:
            return 0.5

        p = (
            0.5
            +
            drift
            *
            self.dt
            /
            (
                2.0
                *
                self.dr
            )
        )

        return float(
            np.clip(
                p,
                0.01,
                0.99
            )
        )

    def build_tree(
        self
    ):
        """
        Build rate nodes and transition probabilities.
        """

        self.rates = []
        self.probabilities = []

        for step in range(
            self.n_steps + 1
        ):

            step_rates = np.array(
                [
                    self.node_rate(
                        step,
                        node
                    )
                    for node in range(step + 1)
                ]
            )

            self.rates.append(
                step_rates
            )

        for step in range(
            self.n_steps
        ):

            step_probs = np.array(
                [
                    self.transition_probability(
                        step,
                        node
                    )
                    for node in range(step + 1)
                ]
            )

            self.probabilities.append(
                step_probs
            )

    def discount_factor_one_step(
        self,
        step,
        node
    ):
        """
        One-step discount factor from a node:

            exp(-r dt)
        """

        r = self.rates[step][node]

        return np.exp(
            -r * self.dt
        )