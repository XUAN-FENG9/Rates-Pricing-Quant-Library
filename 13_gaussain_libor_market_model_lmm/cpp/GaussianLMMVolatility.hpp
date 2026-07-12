#ifndef GAUSSIANLMMVOLATILITY_HPP_INCLUDED
#define GAUSSIANLMMVOLATILITY_HPP_INCLUDED


#include <vector>

#include "Correlation.hpp"

/*
    GaussianLMMVolatility.hpp

    Deterministic normal forward-rate volatility:

        sigma_i(t)
        =
        sigmaLevel
        exp[-decay * (T_i - t)]

    Forward volatility becomes zero after reset.
*/

class GaussianLMMVolatility {

private:

    std::vector<double> resetTimes_;

    double sigmaLevel_;
    double decay_;
    double floor_;

public:

    GaussianLMMVolatility(
        const std::vector<double>& resetTimes,
        double sigmaLevel = 0.01,
        double decay = 0.05,
        double floor = 0.001
    );

    std::vector<double> instantaneousVolatilities(
        double time
    ) const;

    Matrix factorLoadings(
        double time,
        const Matrix& correlationLoadings
    ) const;

    double sigmaLevel() const;

    double decay() const;

    double floor() const;
};

#endif // GAUSSIANLMMVOLATILITY_HPP_INCLUDED
