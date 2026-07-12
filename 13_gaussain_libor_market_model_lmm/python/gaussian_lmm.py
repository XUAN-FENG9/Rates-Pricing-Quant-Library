# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


"""
gaussian_lmm.py

Gaussian LIBOR Market Model under the terminal measure.

This implementation models discrete simple-compounded forward rates:

    L_i(t), i = 0, ..., N - 1

where L_i applies over the tenor interval:

    [T_i, T_{i+1}]

The forward-rate dynamics under the terminal measure Q^{T_N} are:

    dL_i(t)
    =
    mu_i(t) dt
    +
    lambda_i(t) . dW_t

where lambda_i(t) is the normal-volatility factor-loading vector.

For an additive Gaussian LMM, the terminal-measure drift is:

    mu_i(t)
    =
    -
    sum_{j=i+1}^{N-1}
    delta_j
    [lambda_i(t) . lambda_j(t)]
    /
    [1 + delta_j L_j(t)]

The model stores the initial discount factors because terminal-measure
Monte Carlo pricing requires the terminal numeraire P(0, T_N).
"""

import numpy as np


class GaussianLMM:
    """
    Gaussian forward-rate market model.

    Parameters
    ----------
    tenor_structure : TenorStructure
        Discrete tenor structure.

        The model uses:

            tenor_structure.times
            tenor_structure.accruals
            tenor_structure.n_forwards

    initial_forwards : array-like
        Initial simple-compounded forward rates.

        Shape:

            (n_forwards,)

    volatility_model : GaussianLMMVolatility
        Deterministic Gaussian forward-volatility model.

    correlation_loadings : array-like
        Forward-rate factor loading matrix.

        Shape:

            (n_forwards, n_factors)

    initial_discount_factors : array-like
        Initial discount factors on the tenor grid:

            P(0,T_0), P(0,T_1), ..., P(0,T_N)

        Shape:

            (n_forwards + 1,)
    """

    def __init__(
        self,
        tenor_structure,
        initial_forwards,
        volatility_model,
        correlation_loadings,
        initial_discount_factors
    ):

        self.tenor = tenor_structure

        self.initial_forwards = np.asarray(
            initial_forwards,
            dtype=float
        )

        self.volatility_model = (
            volatility_model
        )

        self.correlation_loadings = np.asarray(
            correlation_loadings,
            dtype=float
        )

        self.initial_discount_factors = np.asarray(
            initial_discount_factors,
            dtype=float
        )

        self.n_forwards = (
            self.tenor.n_forwards
        )

        self._validate_inputs()

        self.n_factors = (
            self.correlation_loadings.shape[1]
        )

    def _validate_inputs(
        self
    ):
        """
        Validate model dimensions and initial market inputs.
        """

        if self.initial_forwards.ndim != 1:

            raise ValueError(
                "initial_forwards must be a one-dimensional array."
            )

        if (
            len(self.initial_forwards)
            !=
            self.n_forwards
        ):

            raise ValueError(
                "initial_forwards must contain one forward rate "
                "for each tenor interval."
            )

        if self.correlation_loadings.ndim != 2:

            raise ValueError(
                "correlation_loadings must be a two-dimensional matrix."
            )

        if (
            self.correlation_loadings.shape[0]
            !=
            self.n_forwards
        ):

            raise ValueError(
                "correlation_loadings must contain one row "
                "for each forward rate."
            )

        if (
            self.correlation_loadings.shape[1]
            <=
            0
        ):

            raise ValueError(
                "correlation_loadings must contain at least one factor."
            )

        if self.initial_discount_factors.ndim != 1:

            raise ValueError(
                "initial_discount_factors must be a one-dimensional array."
            )

        if (
            len(self.initial_discount_factors)
            !=
            self.n_forwards + 1
        ):

            raise ValueError(
                "initial_discount_factors must contain one discount factor "
                "for every tenor date."
            )

        if np.any(
            self.initial_discount_factors <= 0.0
        ):

            raise ValueError(
                "All initial discount factors must be positive."
            )

        if not np.isclose(
            self.initial_discount_factors[0],
            1.0,
            atol=1e-8
        ):

            raise ValueError(
                "The first discount factor P(0,T_0) must equal 1."
            )

        if np.any(
            np.diff(
                self.tenor.times
            )
            <=
            0.0
        ):

            raise ValueError(
                "Tenor times must be strictly increasing."
            )

        if np.any(
            self.tenor.accruals
            <=
            0.0
        ):

            raise ValueError(
                "All tenor accrual periods must be positive."
            )

        denominators = (
            1.0
            +
            self.tenor.accruals
            *
            self.initial_forwards
        )

        if np.any(
            denominators <= 0.0
        ):

            raise ValueError(
                "Initial forwards violate "
                "1 + delta_i * L_i > 0."
            )

    def active_mask(
        self,
        t
    ):
        """
        Identify forward rates that have not yet reset.

        Forward L_i becomes fixed at reset time T_i.

        Parameters
        ----------
        t : float
            Current simulation time.

        Returns
        -------
        np.ndarray
            Boolean array with shape:

                (n_forwards,)
        """

        return (
            t
            <
            self.tenor.times[:-1]
            -
            1e-12
        )

    def factor_loadings(
        self,
        t
    ):
        """
        Return time-dependent forward-rate factor loadings.

        The deterministic marginal volatilities are combined with
        the correlation/PCA loadings.

        Parameters
        ----------
        t : float
            Current simulation time.

        Returns
        -------
        np.ndarray
            Loading matrix with shape:

                (n_forwards, n_factors)
        """

        loadings = (
            self.volatility_model.factor_loadings(
                t,
                self.correlation_loadings
            )
        )

        loadings = np.asarray(
            loadings,
            dtype=float
        )

        expected_shape = (
            self.n_forwards,
            self.n_factors
        )

        if loadings.shape != expected_shape:

            raise ValueError(
                "Volatility factor loadings have the wrong shape. "
                f"Expected {expected_shape}, received {loadings.shape}."
            )

        return loadings

    def instantaneous_covariance_matrix(
        self,
        t
    ):
        """
        Return the instantaneous forward-rate covariance matrix.

        If Lambda(t) is the factor-loading matrix, then:

            Sigma(t) = Lambda(t) Lambda(t)^T

        Parameters
        ----------
        t : float
            Current simulation time.

        Returns
        -------
        np.ndarray
            Instantaneous covariance matrix.
        """

        loadings = self.factor_loadings(
            t
        )

        return (
            loadings
            @
            loadings.T
        )

    def validate_forward_state(
        self,
        forward_rates
    ):
        """
        Validate one simulated forward-rate state.

        The discrete discounting relation requires:

            1 + delta_i L_i > 0
        """

        forwards = np.asarray(
            forward_rates,
            dtype=float
        )

        if forwards.shape != (
            self.n_forwards,
        ):

            raise ValueError(
                "forward_rates has the wrong shape."
            )

        denominators = (
            1.0
            +
            self.tenor.accruals
            *
            forwards
        )

        if np.any(
            denominators <= 0.0
        ):

            raise ValueError(
                "Invalid forward state: "
                "1 + delta_i * L_i must remain positive."
            )

        return forwards

    def terminal_measure_drift(
        self,
        t,
        forward_rates
    ):
        """
        Compute terminal-measure drift for one forward-rate state.

        Under the terminal measure Q^{T_N}:

            mu_i(t)
            =
            -
            sum_{j=i+1}^{N-1}
            delta_j
            [lambda_i(t) . lambda_j(t)]
            /
            [1 + delta_j L_j(t)]

        Parameters
        ----------
        t : float
            Current simulation time.

        forward_rates : array-like
            Current forward-rate state.

        Returns
        -------
        np.ndarray
            Drift vector with shape:

                (n_forwards,)
        """

        forwards = self.validate_forward_state(
            forward_rates
        )

        loadings = self.factor_loadings(
            t
        )

        active = self.active_mask(
            t
        )

        drift = np.zeros(
            self.n_forwards
        )

        for i in range(
            self.n_forwards
        ):

            if not active[i]:

                continue

            total = 0.0

            for j in range(
                i + 1,
                self.n_forwards
            ):

                if not active[j]:

                    continue

                covariance_ij = np.dot(
                    loadings[i],
                    loadings[j]
                )

                denominator = (
                    1.0
                    +
                    self.tenor.accruals[j]
                    *
                    forwards[j]
                )

                total += (
                    self.tenor.accruals[j]
                    *
                    covariance_ij
                    /
                    denominator
                )

            drift[i] = -total

        return drift

    def evolve(
        self,
        t,
        forward_rates,
        dt,
        factor_shocks
    ):
        """
        Advance one forward-rate path by one Euler time step.

        Euler discretization:

            L_i(t + dt)
            =
            L_i(t)
            +
            mu_i(t) dt
            +
            lambda_i(t) . Z sqrt(dt)

        Parameters
        ----------
        t : float
            Current simulation time.

        forward_rates : array-like
            Current forward-rate vector.

        dt : float
            Positive simulation time step.

        factor_shocks : array-like
            Independent standard-normal shocks.

            Shape:

                (n_factors,)

        Returns
        -------
        np.ndarray
            Next forward-rate state.
        """

        if dt <= 0.0:

            raise ValueError(
                "dt must be positive."
            )

        forwards = self.validate_forward_state(
            forward_rates
        )

        shocks = np.asarray(
            factor_shocks,
            dtype=float
        )

        if shocks.shape != (
            self.n_factors,
        ):

            raise ValueError(
                "factor_shocks has the wrong shape."
            )

        drift = self.terminal_measure_drift(
            t,
            forwards
        )

        loadings = self.factor_loadings(
            t
        )

        diffusion = (
            loadings
            @
            shocks
            *
            np.sqrt(
                dt
            )
        )

        next_forwards = (
            forwards
            +
            drift
            *
            dt
            +
            diffusion
        )

        active = self.active_mask(
            t
        )

        next_forwards = np.where(
            active,
            next_forwards,
            forwards
        )

        self.validate_forward_state(
            next_forwards
        )

        return next_forwards

    def discount_factors_from_forwards(
        self,
        forward_rates,
        start_index=0
    ):
        """
        Reconstruct tenor-date discount factors from forward rates.

        At tenor date T_k:

            P(T_k,T_k) = 1

        and:

            P(T_k,T_{j+1})
            =
            P(T_k,T_j)
            /
            [1 + delta_j L_j(T_k)]

        Parameters
        ----------
        forward_rates : array-like
            Forward-rate state.

        start_index : int
            Current tenor index k.

        Returns
        -------
        np.ndarray
            Discount factors from T_k to all tenor dates.

            Entries before start_index are set to NaN.
        """

        forwards = self.validate_forward_state(
            forward_rates
        )

        if not (
            0
            <=
            start_index
            <=
            self.n_forwards
        ):

            raise ValueError(
                "start_index is outside the tenor grid."
            )

        discount_factors = np.full(
            self.n_forwards + 1,
            np.nan
        )

        discount_factors[
            start_index
        ] = 1.0

        running_df = 1.0

        for j in range(
            start_index,
            self.n_forwards
        ):

            denominator = (
                1.0
                +
                self.tenor.accruals[j]
                *
                forwards[j]
            )

            running_df /= denominator

            discount_factors[
                j + 1
            ] = running_df

        return discount_factors

    def terminal_bond_from_forwards(
        self,
        forward_rates,
        start_index
    ):
        """
        Return P(T_k,T_N) from a forward-rate state.
        """

        discount_factors = (
            self.discount_factors_from_forwards(
                forward_rates,
                start_index=start_index
            )
        )

        return float(
            discount_factors[-1]
        )

    def initial_terminal_discount_factor(
        self
    ):
        """
        Return the initial terminal bond P(0,T_N).
        """

        return float(
            self.initial_discount_factors[-1]
        )

    def summary(
        self
    ):
        """
        Return model configuration as a dictionary.
        """

        return {
            "model": "Gaussian LIBOR Market Model",
            "measure": "Terminal measure",
            "number_of_forwards": self.n_forwards,
            "number_of_factors": self.n_factors,
            "tenor_start": float(
                self.tenor.times[0]
            ),
            "tenor_end": float(
                self.tenor.times[-1]
            ),
            "terminal_discount_factor": (
                self.initial_terminal_discount_factor()
            ),
            "minimum_initial_forward": float(
                np.min(
                    self.initial_forwards
                )
            ),
            "maximum_initial_forward": float(
                np.max(
                    self.initial_forwards
                )
            )
        }