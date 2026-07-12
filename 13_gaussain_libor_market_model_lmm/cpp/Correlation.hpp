#pragma once

#include <vector>

/*
    Correlation.hpp

    Utilities for:

        exponential correlation matrices
        stable Cholesky decomposition
        PCA factor reduction
*/

using Matrix =
    std::vector<std::vector<double>>;

Matrix exponentialCorrelationMatrix(
    const std::vector<double>& resetTimes,
    double beta
);

Matrix stableCholesky(
    const Matrix& matrix,
    double jitter = 1e-12,
    int maxAttempts = 8
);

Matrix principalComponentLoadings(
    const Matrix& correlationMatrix,
    int numberOfFactors,
    int maxIterations = 1000,
    double tolerance = 1e-12
);

Matrix matrixMultiply(
    const Matrix& left,
    const Matrix& right
);

Matrix transpose(
    const Matrix& matrix
);
