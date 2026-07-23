"""
lmm_sabr_hybrid.py

LMM-SABR hybrid model under the terminal measure.

The model reuses the Chapter 13 components:

    TenorStructure
    GaussianLMMVolatility
    correlation loadings
    PCA factor reduction
    terminal-measure drift structure
    discount-factor reconstruction

The forward-rate dynamics are:

    dL_i(t)
        =
        mu_i(t) dt
        +
        lambda_i(t) . dW_t

where:

    lambda_i(t)
        =
        g_i(t)
        alpha_i(t)
        [L_i(t) + shift_i]^beta_i
        b_i

The stochastic-volatility dynamics are:

    d alpha_i(t)
        =
        nu_i alpha_i(t) dZ_i(t)

with correlation:

    Corr(dW_i, dZ_i) = rho_i.
"""

import numpy as np


class LMMSABRHybrid:
    """
    Terminal-measure LMM-SABR hybrid model.
    """

    def __init__(
        self,
        tenor_structure,
        initial_forwards,
        deterministic_volatility_model,
        correlation_loadings,
        initial_discount_factors,
        sabr_parameters
    ):

        self.tenor = tenor_structure

        self.initial_forwards = np.asarray(
            initial_forwards,
            dtype=float
        )

        self.deterministic_volatility_model = (
            deterministic_volatility_model
        )

        self.correlation_loadings = np.asarray(
            correlation_loadings,
            dtype=float
        )

        self.initial_discount_factors = np.asarray(
            initial_discount_factors,
            dtype=float
        )

        self.sabr_parameters = (
            sabr_parameters
        )

        self.number_of_forwards = len(
            self.initial_forwards
        )

        if self.correlation_loadings.ndim != 2:

            raise ValueError(
                "correlation_loadings must be a matrix."
            )

        self.number_of_factors = (
            self.correlation_loadings.shape[1]
        )

        self.validate_inputs()

    def validate_inputs(
        self
    ):
        """
        Validate model dimensions and initial values.
        """

        if self.number_of_forwards <= 0:

            raise ValueError(
                "At least one forward rate is required."
            )

        if (
            self.correlation_loadings.shape[0]
            !=
            self.number_of_forwards
        ):

            raise ValueError(
                "Correlation loading rows must equal "
                "the number of forwards."
            )

        if self.number_of_factors <= 0:

            raise ValueError(
                "At least one rate factor is required."
            )

        if (
            len(
                self.initial_discount_factors
            )
            !=
            self.number_of_forwards + 1
        ):

            raise ValueError(
                "Initial discount factors must have length "
                "number_of_forwards + 1."
            )

        if np.any(
            self.initial_discount_factors <= 0.0
        ):

            raise ValueError(
                "Initial discount factors must be positive."
            )

        if (
            self.sabr_parameters.number_of_forwards
            !=
            self.number_of_forwards
        ):

            raise ValueError(
                "SABR parameters are inconsistent "
                "with the forward vector."
            )

        accruals = self.get_accruals()

        if len(accruals) != self.number_of_forwards:

            raise ValueError(
                "Tenor accruals are inconsistent "
                "with the forward vector."
            )

        if np.any(
            1.0
            +
            accruals
            *
            self.initial_forwards
            <=
            0.0
        ):

            raise ValueError(
                "Initial forwards violate "
                "1 + delta * L > 0."
            )

        shifted_forwards = (
            self.initial_forwards
            +
            self.sabr_parameters.shift
        )

        if np.any(
            shifted_forwards <= 0.0
        ):

            raise ValueError(
                "Initial forwards plus shifts "
                "must be positive."
            )

    def get_reset_times(
        self
    ):
        """
        Return forward reset times.
        """

        return np.asarray(
            self.tenor.times[:-1],
            dtype=float
        )

    def get_accruals(
        self
    ):
        """
        Return accrual periods.
        """

        return np.asarray(
            self.tenor.accruals,
            dtype=float
        )

    def active_mask(
        self,
        time
    ):
        """
        Identify forwards that have not yet reset.
        """

        return (
            float(time)
            <
            self.get_reset_times()
            -
            1.0e-12
        )

    def deterministic_volatilities(
        self,
        time
    ):
        """
        Reuse the Chapter 13 deterministic volatility term structure.
        """

        return np.asarray(
            self.deterministic_volatility_model
            .instantaneous_vols(
                time
            ),
            dtype=float
        )

    def validate_state(
        self,
        forwards,
        alpha
    ):
        """
        Validate a simulated model state.
        """

        forwards = np.asarray(
            forwards,
            dtype=float
        )

        alpha = np.asarray(
            alpha,
            dtype=float
        )

        if forwards.shape != (
            self.number_of_forwards,
        ):

            raise ValueError(
                "Forward state has the wrong shape."
            )

        if alpha.shape != (
            self.number_of_forwards,
        ):

            raise ValueError(
                "Alpha state has the wrong shape."
            )

        if not np.all(
            np.isfinite(
                forwards
            )
        ):

            raise RuntimeError(
                "Forward state contains invalid values."
            )

        if not np.all(
            np.isfinite(
                alpha
            )
        ):

            raise RuntimeError(
                "Alpha state contains invalid values."
            )

        if np.any(
            alpha <= 0.0
        ):

            raise RuntimeError(
                "All alpha values must be positive."
            )

        if np.any(
            1.0
            +
            self.get_accruals()
            *
            forwards
            <=
            0.0
        ):

            raise RuntimeError(
                "Forward state violates "
                "1 + delta * L > 0."
            )

        if np.any(
            forwards
            +
            self.sabr_parameters.shift
            <=
            0.0
        ):

            raise RuntimeError(
                "Forward state violates "
                "L + shift > 0."
            )

    def factor_loadings(
        self,
        time,
        forwards,
        alpha
    ):
        """
        Calculate SABR-adjusted forward factor loadings.

        Returns
        -------
        numpy.ndarray
            Matrix with shape:

            number_of_forwards
            x
            number_of_factors
        """

        forwards = np.asarray(
            forwards,
            dtype=float
        )

        alpha = np.asarray(
            alpha,
            dtype=float
        )

        self.validate_state(
            forwards,
            alpha
        )

        shifted_forwards = (
            forwards
            +
            self.sabr_parameters.shift
        )

        cev_term = np.power(
            shifted_forwards,
            self.sabr_parameters.beta
        )

        volatility_scale = (
            self.deterministic_volatilities(
                time
            )
            *
            alpha
            *
            cev_term
        )

        active = self.active_mask(
            time
        )

        volatility_scale = np.where(
            active,
            volatility_scale,
            0.0
        )

        return (
            volatility_scale[:, None]
            *
            self.correlation_loadings
        )

    def instantaneous_covariance_matrix(
        self,
        time,
        forwards,
        alpha
    ):
        """
        Calculate the instantaneous forward covariance matrix.
        """

        loadings = self.factor_loadings(
            time,
            forwards,
            alpha
        )

        return (
            loadings
            @
            loadings.T
        )

    def terminal_measure_drift(
        self,
        time,
        forwards,
        alpha
    ):
        """
        Calculate terminal-measure forward drifts.

        The drift is:

            mu_i
                =
                - sum over j > i
                  delta_j
                  lambda_i . lambda_j
                  /
                  (1 + delta_j L_j)
        """

        forwards = np.asarray(
            forwards,
            dtype=float
        )

        alpha = np.asarray(
            alpha,
            dtype=float
        )

        self.validate_state(
            forwards,
            alpha
        )

        loadings = self.factor_loadings(
            time,
            forwards,
            alpha
        )

        active = self.active_mask(
            time
        )

        accruals = self.get_accruals()

        drift = np.zeros(
            self.number_of_forwards
        )

        for i in range(
            self.number_of_forwards
        ):

            if not active[i]:

                continue

            total = 0.0

            for j in range(
                i + 1,
                self.number_of_forwards
            ):

                if not active[j]:

                    continue

                denominator = (
                    1.0
                    +
                    accruals[j]
                    *
                    forwards[j]
                )

                if denominator <= 0.0:

                    raise RuntimeError(
                        "Invalid denominator in drift calculation."
                    )

                covariance = np.dot(
                    loadings[i],
                    loadings[j]
                )

                total += (
                    accruals[j]
                    *
                    covariance
                    /
                    denominator
                )

            drift[i] = -total

        return drift

    def effective_forward_shocks(
        self,
        time,
        forwards,
        alpha,
        rate_factor_shocks
    ):
        """
        Convert common factor shocks into one normalized shock
        for every forward rate.

        These shocks are used to create correlation between:

            forward-rate changes

        and:

            alpha changes.
        """

        rate_factor_shocks = np.asarray(
            rate_factor_shocks,
            dtype=float
        )

        if rate_factor_shocks.shape != (
            self.number_of_factors,
        ):

            raise ValueError(
                "rate_factor_shocks has the wrong shape."
            )

        loadings = self.factor_loadings(
            time,
            forwards,
            alpha
        )

        raw_forward_shocks = (
            loadings
            @
            rate_factor_shocks
        )

        loading_norms = np.linalg.norm(
            loadings,
            axis=1
        )

        normalized_shocks = np.zeros(
            self.number_of_forwards
        )

        non_zero = (
            loading_norms > 1.0e-16
        )

        normalized_shocks[non_zero] = (
            raw_forward_shocks[non_zero]
            /
            loading_norms[non_zero]
        )

        return normalized_shocks

    def evolve(
        self,
        time,
        forwards,
        alpha,
        dt,
        rate_factor_shocks,
        independent_volatility_shocks
    ):
        """
        Advance forwards and stochastic volatilities by one time step.

        Forward rates use an Euler step.

        Alpha uses an exact lognormal step.
        """

        if dt <= 0.0:

            raise ValueError(
                "dt must be positive."
            )

        forwards = np.asarray(
            forwards,
            dtype=float
        )

        alpha = np.asarray(
            alpha,
            dtype=float
        )

        rate_factor_shocks = np.asarray(
            rate_factor_shocks,
            dtype=float
        )

        independent_volatility_shocks = np.asarray(
            independent_volatility_shocks,
            dtype=float
        )

        self.validate_state(
            forwards,
            alpha
        )

        if rate_factor_shocks.shape != (
            self.number_of_factors,
        ):

            raise ValueError(
                "rate_factor_shocks has the wrong shape."
            )

        if (
            independent_volatility_shocks.shape
            !=
            (
                self.number_of_forwards,
            )
        ):

            raise ValueError(
                "independent_volatility_shocks "
                "has the wrong shape."
            )

        active = self.active_mask(
            time
        )

        loadings = self.factor_loadings(
            time,
            forwards,
            alpha
        )

        drift = self.terminal_measure_drift(
            time,
            forwards,
            alpha
        )

        square_root_dt = np.sqrt(
            dt
        )

        diffusion = (
            loadings
            @
            rate_factor_shocks
            *
            square_root_dt
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
        
        next_forwards = np.where(
            active,
            next_forwards,
            forwards
        )
        
        # Keep the shifted forward strictly positive.
        minimum_forwards = (
            -self.sabr_parameters.shift
            +
            1.0e-8
        )
        
        next_forwards = np.where(
            active,
            np.maximum(
                next_forwards,
                minimum_forwards
            ),
            forwards
        )

        effective_rate_shocks = (
            self.effective_forward_shocks(
                time,
                forwards,
                alpha,
                rate_factor_shocks
            )
        )

        rho = self.sabr_parameters.rho

        correlated_volatility_shocks = (
            rho
            *
            effective_rate_shocks
            +
            np.sqrt(
                1.0
                -
                rho
                *
                rho
            )
            *
            independent_volatility_shocks
        )

        nu = self.sabr_parameters.nu

        alpha_log_increment = (
            -0.5
            *
            nu
            *
            nu
            *
            dt
            +
            nu
            *
            square_root_dt
            *
            correlated_volatility_shocks
        )

        next_alpha = (
            alpha
            *
            np.exp(
                alpha_log_increment
            )
        )

        next_alpha = np.clip(
            next_alpha,
            self.sabr_parameters.alpha_floor,
            self.sabr_parameters.alpha_cap
        )

        next_alpha = np.where(
            active,
            next_alpha,
            alpha
        )

        self.validate_state(
            next_forwards,
            next_alpha
        )

        return (
            next_forwards,
            next_alpha
        )

    def discount_factors_from_forwards(
        self,
        forwards,
        start_index
    ):
        """
        Reconstruct discount factors from a forward curve.

        Starting from:

            P(T_k, T_k) = 1

        use:

            P(T_k, T_{j+1})
                =
                P(T_k, T_j)
                /
                (1 + delta_j L_j)
        """

        forwards = np.asarray(
            forwards,
            dtype=float
        )

        if forwards.shape != (
            self.number_of_forwards,
        ):

            raise ValueError(
                "Forward state has the wrong shape."
            )

        if (
            start_index < 0
            or
            start_index > self.number_of_forwards
        ):

            raise ValueError(
                "start_index is outside the tenor grid."
            )

        discount_factors = np.full(
            self.number_of_forwards + 1,
            np.nan
        )

        discount_factors[start_index] = 1.0

        running_discount_factor = 1.0

        accruals = self.get_accruals()

        for j in range(
            start_index,
            self.number_of_forwards
        ):

            denominator = (
                1.0
                +
                accruals[j]
                *
                forwards[j]
            )

            if denominator <= 0.0:

                raise RuntimeError(
                    "Cannot reconstruct discount factors "
                    "from an invalid forward state."
                )

            running_discount_factor /= (
                denominator
            )

            discount_factors[j + 1] = (
                running_discount_factor
            )

        return discount_factors

    def terminal_bond_from_forwards(
        self,
        forwards,
        start_index
    ):
        """
        Return P(T_k, T_N).
        """

        discount_factors = (
            self.discount_factors_from_forwards(
                forwards,
                start_index
            )
        )

        return float(
            discount_factors[-1]
        )

    def initial_terminal_discount_factor(
        self
    ):
        """
        Return P(0, T_N).
        """

        return float(
            self.initial_discount_factors[-1]
        )

    def summary(
        self
    ):
        """
        Return a compact model summary.
        """

        return {
            "model":
                "LMM-SABR Hybrid",

            "number_of_forwards":
                self.number_of_forwards,

            "number_of_rate_factors":
                self.number_of_factors,

            "initial_terminal_discount_factor":
                self.initial_terminal_discount_factor(),

            "sabr_parameters":
                self.sabr_parameters.summary()
        }