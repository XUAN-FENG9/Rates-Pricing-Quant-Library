#include "Correlation.hpp"

#include <algorithm>
#include <cmath>
#include <random>
#include <stdexcept>

/*
    Exponential correlation:

        rho_ij = exp(-beta * |T_i - T_j|)
*/

Matrix exponentialCorrelationMatrix(
    const std::vector<double>& resetTimes,
    double beta
){

    if(beta < 0.0){

        throw std::invalid_argument(
            "Correlation decay beta must be non-negative."
        );
    }

    int n =
        static_cast<int>(
            resetTimes.size()
        );

    Matrix correlation(
        n,
        std::vector<double>(
            n,
            0.0
        )
    );

    for(int i = 0; i < n; ++i){

        for(int j = 0; j < n; ++j){

            correlation[i][j] =
                std::exp(
                    -beta
                    *
                    std::abs(
                        resetTimes[i]
                        -
                        resetTimes[j]
                    )
                );
        }
    }

    return correlation;
}

/*
    Matrix transpose.
*/

Matrix transpose(
    const Matrix& matrix
){

    if(matrix.empty()){

        return {};
    }

    int rows =
        static_cast<int>(
            matrix.size()
        );

    int columns =
        static_cast<int>(
            matrix[0].size()
        );

    Matrix result(
        columns,
        std::vector<double>(
            rows,
            0.0
        )
    );

    for(int i = 0; i < rows; ++i){

        for(int j = 0; j < columns; ++j){

            result[j][i] =
                matrix[i][j];
        }
    }

    return result;
}

/*
    Matrix multiplication.
*/

Matrix matrixMultiply(
    const Matrix& left,
    const Matrix& right
){

    if(left.empty() || right.empty()){

        return {};
    }

    int leftRows =
        static_cast<int>(
            left.size()
        );

    int leftColumns =
        static_cast<int>(
            left[0].size()
        );

    int rightRows =
        static_cast<int>(
            right.size()
        );

    int rightColumns =
        static_cast<int>(
            right[0].size()
        );

    if(leftColumns != rightRows){

        throw std::invalid_argument(
            "Incompatible matrix dimensions."
        );
    }

    Matrix result(
        leftRows,
        std::vector<double>(
            rightColumns,
            0.0
        )
    );

    for(int i = 0; i < leftRows; ++i){

        for(int k = 0; k < leftColumns; ++k){

            for(int j = 0; j < rightColumns; ++j){

                result[i][j] +=
                    left[i][k]
                    *
                    right[k][j];
            }
        }
    }

    return result;
}

/*
    Stable Cholesky decomposition.
*/

Matrix stableCholesky(
    const Matrix& matrix,
    double jitter,
    int maxAttempts
){

    int n =
        static_cast<int>(
            matrix.size()
        );

    if(n == 0){

        return {};
    }

    for(const auto& row : matrix){

        if(static_cast<int>(row.size()) != n){

            throw std::invalid_argument(
                "Cholesky requires a square matrix."
            );
        }
    }

    double currentJitter =
        jitter;

    for(int attempt = 0; attempt < maxAttempts; ++attempt){

        Matrix lower(
            n,
            std::vector<double>(
                n,
                0.0
            )
        );

        bool success =
            true;

        for(int i = 0; i < n && success; ++i){

            for(int j = 0; j <= i; ++j){

                double sum =
                    matrix[i][j];

                if(i == j){

                    sum +=
                        currentJitter;
                }

                for(int k = 0; k < j; ++k){

                    sum -=
                        lower[i][k]
                        *
                        lower[j][k];
                }

                if(i == j){

                    if(sum <= 0.0){

                        success =
                            false;

                        break;
                    }

                    lower[i][j] =
                        std::sqrt(
                            sum
                        );

                } else {

                    lower[i][j] =
                        sum
                        /
                        lower[j][j];
                }
            }
        }

        if(success){

            return lower;
        }

        currentJitter *=
            10.0;
    }

    throw std::runtime_error(
        "Cholesky decomposition failed."
    );
}

/*
    Dot product.
*/

static double dotProduct(
    const std::vector<double>& left,
    const std::vector<double>& right
){

    double result =
        0.0;

    for(std::size_t i = 0; i < left.size(); ++i){

        result +=
            left[i]
            *
            right[i];
    }

    return result;
}

/*
    Normalize vector.
*/

static void normalizeVector(
    std::vector<double>& vector
){

    double norm =
        std::sqrt(
            dotProduct(
                vector,
                vector
            )
        );

    if(norm < 1e-16){

        throw std::runtime_error(
            "Cannot normalize a near-zero vector."
        );
    }

    for(double& value : vector){

        value /=
            norm;
    }
}

/*
    Matrix-vector multiplication.
*/

static std::vector<double> matrixVectorMultiply(
    const Matrix& matrix,
    const std::vector<double>& vector
){

    std::vector<double> result(
        matrix.size(),
        0.0
    );

    for(std::size_t i = 0; i < matrix.size(); ++i){

        result[i] =
            dotProduct(
                matrix[i],
                vector
            );
    }

    return result;
}

/*
    PCA loadings using power iteration with deflation.

    This is an educational implementation.

    For production code, use Eigen, LAPACK, or another numerical library.
*/

Matrix principalComponentLoadings(
    const Matrix& correlationMatrix,
    int numberOfFactors,
    int maxIterations,
    double tolerance
){

    int n =
        static_cast<int>(
            correlationMatrix.size()
        );

    if(n == 0){

        return {};
    }

    numberOfFactors =
        std::min(
            numberOfFactors,
            n
        );

    Matrix workingMatrix =
        correlationMatrix;

    Matrix loadings(
        n,
        std::vector<double>(
            numberOfFactors,
            0.0
        )
    );

    std::mt19937 generator(
        42
    );

    std::uniform_real_distribution<double> uniform(
        -1.0,
        1.0
    );

    for(int factor = 0; factor < numberOfFactors; ++factor){

        std::vector<double> eigenvector(
            n,
            0.0
        );

        for(double& value : eigenvector){

            value =
                uniform(
                    generator
                );
        }

        normalizeVector(
            eigenvector
        );

        for(int iteration = 0; iteration < maxIterations; ++iteration){

            std::vector<double> nextVector =
                matrixVectorMultiply(
                    workingMatrix,
                    eigenvector
                );

            normalizeVector(
                nextVector
            );

            double difference =
                0.0;

            for(int i = 0; i < n; ++i){

                double delta =
                    nextVector[i]
                    -
                    eigenvector[i];

                difference +=
                    delta
                    *
                    delta;
            }

            eigenvector =
                nextVector;

            if(std::sqrt(difference) < tolerance){

                break;
            }
        }

        std::vector<double> matrixTimesVector =
            matrixVectorMultiply(
                workingMatrix,
                eigenvector
            );

        double eigenvalue =
            dotProduct(
                eigenvector,
                matrixTimesVector
            );

        eigenvalue =
            std::max(
                eigenvalue,
                0.0
            );

        double scale =
            std::sqrt(
                eigenvalue
            );

        for(int i = 0; i < n; ++i){

            loadings[i][factor] =
                eigenvector[i]
                *
                scale;
        }

        /*
            Deflation:

                A_new = A - lambda * v * v^T
        */

        for(int i = 0; i < n; ++i){

            for(int j = 0; j < n; ++j){

                workingMatrix[i][j] -=
                    eigenvalue
                    *
                    eigenvector[i]
                    *
                    eigenvector[j];
            }
        }
    }

    return loadings;
}
