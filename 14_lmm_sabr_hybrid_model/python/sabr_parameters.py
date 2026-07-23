"""
sabr_parameters.py

SABR parameter container for the LMM-SABR hybrid model.

The model assigns the following parameters to each forward rate:

    alpha0
        Initial stochastic volatility.

    beta
        CEV elasticity parameter.

    rho
        Correlation between the forward-rate shock and
        the stochastic-volatility shock.

    nu
        Volatility of volatility.

    shift
        Positive displacement applied to the forward rate.

All inputs may be either:

    a scalar

or:

    a one-dimensional array with one value per forward.
"""

import numpy as np


def expand_parameter(
    value,
    number_of_forwards,
    parameter_name
):
    """
    Expand a scalar parameter into a vector.

    Parameters
    ----------
    value : float or array-like
        Scalar or one value per forward.

    number_of_forwards : int
        Number of modeled forward rates.

    parameter_name : str
        Parameter name used in error messages.

    Returns
    -------
    numpy.ndarray
        Parameter vector.
    """

    parameter = np.asarray(
        value,
        dtype=float
    )

    if parameter.ndim == 0:

        parameter = np.full(
            number_of_forwards,
            float(parameter)
        )

    if parameter.ndim != 1:

        raise ValueError(
            f"{parameter_name} must be a scalar "
            "or a one-dimensional array."
        )

    if len(parameter) != number_of_forwards:

        raise ValueError(
            f"{parameter_name} must contain "
            f"{number_of_forwards} values."
        )

    if not np.all(
        np.isfinite(
            parameter
        )
    ):

        raise ValueError(
            f"{parameter_name} contains non-finite values."
        )

    return parameter


class SABRParameters:
    """
    Store forward-specific SABR parameters.
    """

    def __init__(
        self,
        number_of_forwards,
        alpha0=0.18,
        beta=0.50,
        rho=-0.25,
        nu=0.40,
        shift=0.03,
        alpha_floor=1.0e-8,
        alpha_cap=10.0
    ):

        if number_of_forwards <= 0:

            raise ValueError(
                "number_of_forwards must be positive."
            )

        self.number_of_forwards = (
            int(
                number_of_forwards
            )
        )

        self.alpha0 = expand_parameter(
            alpha0,
            self.number_of_forwards,
            "alpha0"
        )

        self.beta = expand_parameter(
            beta,
            self.number_of_forwards,
            "beta"
        )

        self.rho = expand_parameter(
            rho,
            self.number_of_forwards,
            "rho"
        )

        self.nu = expand_parameter(
            nu,
            self.number_of_forwards,
            "nu"
        )

        self.shift = expand_parameter(
            shift,
            self.number_of_forwards,
            "shift"
        )

        self.alpha_floor = float(
            alpha_floor
        )

        self.alpha_cap = float(
            alpha_cap
        )

        self.validate()

    def validate(
        self
    ):
        """
        Validate parameter restrictions.
        """

        if np.any(
            self.alpha0 <= 0.0
        ):

            raise ValueError(
                "alpha0 must be strictly positive."
            )

        if np.any(
            self.beta < 0.0
        ) or np.any(
            self.beta > 1.0
        ):

            raise ValueError(
                "beta must lie between 0 and 1."
            )

        if np.any(
            self.rho <= -1.0
        ) or np.any(
            self.rho >= 1.0
        ):

            raise ValueError(
                "rho must lie strictly between -1 and 1."
            )

        if np.any(
            self.nu < 0.0
        ):

            raise ValueError(
                "nu must be non-negative."
            )

        if np.any(
            self.shift < 0.0
        ):

            raise ValueError(
                "shift must be non-negative."
            )

        if self.alpha_floor <= 0.0:

            raise ValueError(
                "alpha_floor must be positive."
            )

        if self.alpha_cap <= self.alpha_floor:

            raise ValueError(
                "alpha_cap must be greater than alpha_floor."
            )

    def summary(
        self
    ):
        """
        Return a dictionary containing parameter ranges.
        """

        return {
            "number_of_forwards":
                self.number_of_forwards,

            "alpha0_min":
                float(
                    np.min(
                        self.alpha0
                    )
                ),

            "alpha0_max":
                float(
                    np.max(
                        self.alpha0
                    )
                ),

            "beta_min":
                float(
                    np.min(
                        self.beta
                    )
                ),

            "beta_max":
                float(
                    np.max(
                        self.beta
                    )
                ),

            "rho_min":
                float(
                    np.min(
                        self.rho
                    )
                ),

            "rho_max":
                float(
                    np.max(
                        self.rho
                    )
                ),

            "nu_min":
                float(
                    np.min(
                        self.nu
                    )
                ),

            "nu_max":
                float(
                    np.max(
                        self.nu
                    )
                ),

            "shift_min":
                float(
                    np.min(
                        self.shift
                    )
                ),

            "shift_max":
                float(
                    np.max(
                        self.shift
                    )
                )
        }
