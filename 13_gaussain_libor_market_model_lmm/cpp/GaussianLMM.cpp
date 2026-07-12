#include "GaussianLMM.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

GaussianLMM::GaussianLMM(
    const TenorStructure& tenor,
    const std::vector<double>& initialForwards,
    const GaussianLMMVolatility& volatilityModel,
    const Matrix& correlationLoadings,
    const std::vector<double>& initialDiscountFactors
)
    :
    tenor_(tenor),
    initialForwards_(initialForwards),
    initialDiscountFactors_(initialDiscountFactors),
    volatilityModel_(volatilityModel),
    correlationLoadings_(correlationLoadings),
    numberOfFactors_(
        correlationLoadings.empty()
        ?
        0
        :
        static_cast<int>(
            correlationLoadings[0].size()
        )
    )
{

    validateInputs();
}

void GaussianLMM::validateInputs() const {

    if(
        static_cast<int>(
            initialForwards_.size()
        )
        !=
        tenor_.numberOfForwards()
    ){

        throw std::invalid_argument(
            "Initial-forward vector has the wrong size."
        );
    }

    if(
        static_cast<int>(
            initialDiscountFactors_.size()
        )
        !=
        tenor_.numberOfForwards() + 1
    ){

        throw std::invalid_argument(
            "Initial discount-factor vector has the wrong size."
        );
    }

    if(
        static_cast<int>(
            correlationLoadings_.size()
        )
        !=
        tenor_.numberOfForwards()
    ){

        throw std::invalid_argument(
            "Correlation loadings have the wrong number of rows."
        );
    }

    if(numberOfFactors_ <= 0){

        throw std::invalid_argument(
            "At least one LMM factor is required."
        );
    }

    for(const auto& row : correlationLoadings_){

        if(
            static_cast<int>(
                row.size()
            )
            !=
            numberOfFactors_
        ){

            throw std::invalid_argument(
                "Correlation-loading rows must have equal length."
            );
        }
    }

    for(double discountFactor : initialDiscountFactors_){

        if(discountFactor <= 0.0){

            throw std::invalid_argument(
                "Initial discount factors must be positive."
            );
        }
    }

    const std::vector<double>& accruals =
        tenor_.accruals();

    for(int i = 0; i < tenor_.numberOfForwards(); ++i){

        if(
            1.0
            +
            accruals[i]
            *
            initialForwards_[i]
            <=
            0.0
        ){

            throw std::invalid_argument(
                "Initial forward state violates 1 + delta * L > 0."
            );
        }
    }
}

const TenorStructure& GaussianLMM::tenor() const {

    return tenor_;
}

const std::vector<double>& GaussianLMM::initialForwards() const {

    return initialForwards_;
}

const std::vector<double>&
GaussianLMM::initialDiscountFactors() const {

    return initialDiscountFactors_;
}

int GaussianLMM::numberOfForwards() const {

    return tenor_.numberOfForwards();
}

int GaussianLMM::numberOfFactors() const {

    return numberOfFactors_;
}

std::vector<bool> GaussianLMM::activeMask(
    double time
) const {

    std::vector<bool> active(
        numberOfForwards(),
        false
    );

    const std::vector<double>& resetTimes =
        tenor_.times();

    for(int i = 0; i < numberOfForwards(); ++i){

        active[i] =
            time
            <
            resetTimes[i]
            -
            1e-12;
    }

    return active;
}

Matrix GaussianLMM::factorLoadings(
    double time
) const {

    return volatilityModel_.factorLoadings(
        time,
        correlationLoadings_
    );
}

Matrix GaussianLMM::instantaneousCovarianceMatrix(
    double time
) const {

    Matrix loadings =
        factorLoadings(
            time
        );

    return matrixMultiply(
        loadings,
        transpose(loadings)
    );
}

std::vector<double> GaussianLMM::terminalMeasureDrift(
    double time,
    const std::vector<double>& forwards
) const {

    if(
        static_cast<int>(
            forwards.size()
        )
        !=
        numberOfForwards()
    ){

        throw std::invalid_argument(
            "Forward state has the wrong length."
        );
    }

    Matrix loadings =
        factorLoadings(
            time
        );

    std::vector<bool> active =
        activeMask(
            time
        );

    const std::vector<double>& accruals =
        tenor_.accruals();

    std::vector<double> drift(
        numberOfForwards(),
        0.0
    );

    for(int i = 0; i < numberOfForwards(); ++i){

        if(!active[i]){

            continue;
        }

        double total =
            0.0;

        for(int j = i + 1; j < numberOfForwards(); ++j){

            if(!active[j]){

                continue;
            }

            double covariance =
                0.0;

            for(int factor = 0; factor < numberOfFactors_; ++factor){

                covariance +=
                    loadings[i][factor]
                    *
                    loadings[j][factor];
            }

            double denominator =
                1.0
                +
                accruals[j]
                *
                forwards[j];

            if(denominator <= 0.0){

                throw std::runtime_error(
                    "Invalid simulated forward state."
                );
            }

            total +=
                accruals[j]
                *
                covariance
                /
                denominator;
        }

        drift[i] =
            -total;
    }

    return drift;
}

std::vector<double> GaussianLMM::evolve(
    double time,
    const std::vector<double>& forwards,
    double dt,
    const std::vector<double>& factorShocks
) const {

    if(dt <= 0.0){

        throw std::invalid_argument(
            "Simulation time step must be positive."
        );
    }

    if(
        static_cast<int>(
            factorShocks.size()
        )
        !=
        numberOfFactors_
    ){

        throw std::invalid_argument(
            "Factor-shock vector has the wrong size."
        );
    }

    std::vector<double> drift =
        terminalMeasureDrift(
            time,
            forwards
        );

    Matrix loadings =
        factorLoadings(
            time
        );

    std::vector<bool> active =
        activeMask(
            time
        );

    std::vector<double> nextForwards =
        forwards;

    double squareRootDt =
        std::sqrt(
            dt
        );

    for(int i = 0; i < numberOfForwards(); ++i){

        if(!active[i]){

            continue;
        }

        double diffusion =
            0.0;

        for(int factor = 0; factor < numberOfFactors_; ++factor){

            diffusion +=
                loadings[i][factor]
                *
                factorShocks[factor];
        }

        nextForwards[i] =
            forwards[i]
            +
            drift[i]
            *
            dt
            +
            diffusion
            *
            squareRootDt;

        double denominator =
            1.0
            +
            tenor_.accruals()[i]
            *
            nextForwards[i];

        if(denominator <= 0.0){

            throw std::runtime_error(
                "Euler step produced an invalid forward state."
            );
        }
    }

    return nextForwards;
}

std::vector<double> GaussianLMM::discountFactorsFromForwards(
    const std::vector<double>& forwards,
    int startIndex
) const {

    if(
        startIndex < 0
        ||
        startIndex > numberOfForwards()
    ){

        throw std::invalid_argument(
            "Invalid discount-factor start index."
        );
    }

    std::vector<double> discountFactors(
        numberOfForwards() + 1,
        std::numeric_limits<double>::quiet_NaN()
    );

    discountFactors[startIndex] =
        1.0;

    double runningDiscountFactor =
        1.0;

    for(int j = startIndex; j < numberOfForwards(); ++j){

        double denominator =
            1.0
            +
            tenor_.accruals()[j]
            *
            forwards[j];

        if(denominator <= 0.0){

            throw std::runtime_error(
                "Cannot reconstruct discount factors."
            );
        }

        runningDiscountFactor /=
            denominator;

        discountFactors[j + 1] =
            runningDiscountFactor;
    }

    return discountFactors;
}

double GaussianLMM::terminalBondFromForwards(
    const std::vector<double>& forwards,
    int startIndex
) const {

    return discountFactorsFromForwards(
        forwards,
        startIndex
    ).back();
}

double GaussianLMM::initialTerminalDiscountFactor() const {

    return initialDiscountFactors_.back();
}
