#ifndef GAUSSIANLMM_HPP_INCLUDED
#define GAUSSIANLMM_HPP_INCLUDED

#include <vector>

#include "Correlation.hpp"
#include "GaussianLMMVolatility.hpp"
#include "TenorStructure.hpp"

/*
    GaussianLMM.hpp

    Additive Gaussian LMM under the terminal measure.

    Dynamics:

        dL_i
        =
        mu_i dt
        +
        lambda_i . dW

    Terminal-measure drift:

        mu_i
        =
        -
        sum_{j=i+1}^{N-1}
        delta_j
        (lambda_i . lambda_j)
        /
        (1 + delta_j L_j)
*/

class GaussianLMM {

private:

    TenorStructure tenor_;

    std::vector<double> initialForwards_;
    std::vector<double> initialDiscountFactors_;

    GaussianLMMVolatility volatilityModel_;

    Matrix correlationLoadings_;

    int numberOfFactors_;

    void validateInputs() const;

public:

    GaussianLMM(
        const TenorStructure& tenor,
        const std::vector<double>& initialForwards,
        const GaussianLMMVolatility& volatilityModel,
        const Matrix& correlationLoadings,
        const std::vector<double>& initialDiscountFactors
    );

    const TenorStructure& tenor() const;

    const std::vector<double>& initialForwards() const;

    const std::vector<double>& initialDiscountFactors() const;

    int numberOfForwards() const;

    int numberOfFactors() const;

    std::vector<bool> activeMask(
        double time
    ) const;

    Matrix factorLoadings(
        double time
    ) const;

    Matrix instantaneousCovarianceMatrix(
        double time
    ) const;

    std::vector<double> terminalMeasureDrift(
        double time,
        const std::vector<double>& forwards
    ) const;

    std::vector<double> evolve(
        double time,
        const std::vector<double>& forwards,
        double dt,
        const std::vector<double>& factorShocks
    ) const;

    std::vector<double> discountFactorsFromForwards(
        const std::vector<double>& forwards,
        int startIndex
    ) const;

    double terminalBondFromForwards(
        const std::vector<double>& forwards,
        int startIndex
    ) const;

    double initialTerminalDiscountFactor() const;
};

#endif // GAUSSIANLMM_HPP_INCLUDED
