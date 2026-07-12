#include "GaussianLMMVolatility.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>

GaussianLMMVolatility::GaussianLMMVolatility(
    const std::vector<double>& resetTimes,
    double sigmaLevel,
    double decay,
    double floor
)
    :
    resetTimes_(resetTimes),
    sigmaLevel_(sigmaLevel),
    decay_(decay),
    floor_(floor)
{

    if(sigmaLevel_ < 0.0){

        throw std::invalid_argument(
            "Sigma level must be non-negative."
        );
    }

    if(decay_ < 0.0){

        throw std::invalid_argument(
            "Volatility decay must be non-negative."
        );
    }

    if(floor_ < 0.0){

        throw std::invalid_argument(
            "Volatility floor must be non-negative."
        );
    }
}

std::vector<double>
GaussianLMMVolatility::instantaneousVolatilities(
    double time
) const {

    std::vector<double> volatilities(
        resetTimes_.size(),
        0.0
    );

    for(std::size_t i = 0; i < resetTimes_.size(); ++i){

        if(time >= resetTimes_[i] - 1e-12){

            volatilities[i] =
                0.0;

            continue;
        }

        double remaining =
            resetTimes_[i]
            -
            time;

        double volatility =
            sigmaLevel_
            *
            std::exp(
                -decay_
                *
                remaining
            );

        volatilities[i] =
            std::max(
                volatility,
                floor_
            );
    }

    return volatilities;
}

Matrix GaussianLMMVolatility::factorLoadings(
    double time,
    const Matrix& correlationLoadings
) const {

    std::vector<double> volatilities =
        instantaneousVolatilities(
            time
        );

    if(correlationLoadings.size() != volatilities.size()){

        throw std::invalid_argument(
            "Correlation-loading row count is inconsistent."
        );
    }

    Matrix result =
        correlationLoadings;

    for(std::size_t i = 0; i < result.size(); ++i){

        for(double& value : result[i]){

            value *=
                volatilities[i];
        }
    }

    return result;
}

double GaussianLMMVolatility::sigmaLevel() const {

    return sigmaLevel_;
}

double GaussianLMMVolatility::decay() const {

    return decay_;
}

double GaussianLMMVolatility::floor() const {

    return floor_;
}
