# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


"""
correlation.py

Forward-rate correlation utilities.

A common LMM specification is:

    rho_ij = exp(-beta |T_i - T_j|)

where beta controls correlation decay across maturities.
"""

import numpy as np


def exponential_correlation_matrix(
    reset_times,
    beta=0.10
):
    """
    Build exponential forward-rate correlation matrix.

    Parameters
    ----------
    reset_times : array-like
        Forward reset times T_i.

    beta : float
        Correlation-decay parameter.

        Low beta:
            persistent correlation across maturities.

        High beta:
            faster correlation decay.

    Returns
    -------
    np.ndarray
        Positive-definite correlation matrix.
    """

    reset_times = np.asarray(
        reset_times,
        dtype=float
    )

    if beta < 0.0:
        raise ValueError(
            "beta must be non-negative."
        )

    distances = np.abs(
        reset_times[:, None]
        -
        reset_times[None, :]
    )

    return np.exp(
        -beta
        *
        distances
    )


def stable_cholesky(
    matrix,
    jitter=1e-12,
    max_attempts=8
):
    """
    Compute numerically stable Cholesky factor.

    Small diagonal jitter is added if required.
    """

    matrix = np.asarray(
        matrix,
        dtype=float
    )

    identity = np.eye(
        matrix.shape[0]
    )

    current_jitter = jitter

    for _ in range(
        max_attempts
    ):

        try:

            return np.linalg.cholesky(
                matrix
                +
                current_jitter
                *
                identity
            )

        except np.linalg.LinAlgError:

            current_jitter *= 10.0

    raise np.linalg.LinAlgError(
        "Correlation matrix is not numerically positive definite."
    )


def principal_component_loadings(
    correlation_matrix,
    n_factors
):
    """
    Produce reduced-factor correlation loadings with PCA.

    Parameters
    ----------
    correlation_matrix : np.ndarray
        Full forward-rate correlation matrix.

    n_factors : int
        Number of retained factors.

    Returns
    -------
    np.ndarray
        Loading matrix with shape:

            n_forwards x n_factors
    """

    eigenvalues, eigenvectors = np.linalg.eigh(
        correlation_matrix
    )

    order = np.argsort(
        eigenvalues
    )[::-1]

    eigenvalues = eigenvalues[
        order
    ]

    eigenvectors = eigenvectors[
        :,
        order
    ]

    n_factors = min(
        n_factors,
        correlation_matrix.shape[0]
    )

    selected_values = np.maximum(
        eigenvalues[:n_factors],
        0.0
    )

    selected_vectors = eigenvectors[
        :,
        :n_factors
    ]

    return (
        selected_vectors
        *
        np.sqrt(
            selected_values
        )
    )