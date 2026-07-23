#include "LMMSABRHybrid.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>


LMMSABRHybrid::LMMSABRHybrid(
    const Vector& resetTimes,
    const Vector& accruals,
    const Vector& initialForwards,
    const Vector& initialDiscountFactors,
    const Matrix& correlationLoadings,
    const SABRParameters& sabrParameters,
    double volatilityLevel,
    double volatilityDecay,
    double volatilityFloor
)
    :
    resetTimes_(resetTimes),
    accruals_(accruals),
    initialForwards_(initialForwards),
    initialDiscountFactors_(
        initialDiscountFactors
    ),
    correlationLoadings_(
        correlationLoadings
    ),
    sabrParameters_(
        sabrParameters
    ),
    volatilityLevel_(
        volatilityLevel
    ),
    volatilityDecay_(
        volatilityDecay
    ),
    volatilityFloor_(
        volatilityFloor
    ),
    numberOfForwards_(
        initialForwards.size()
    ),
    numberOfFactors_(
        correlationLoadings.empty()
        ?
        0
        :
        correlationLoadings.front().size()
    )
{
    validateModelInputs();

    validateState(
        initialForwards_,
        sabrParameters_.alpha0()
    );
}


std::size_t LMMSABRHybrid::numberOfForwards() const
{
    return numberOfForwards_;
}


std::size_t LMMSABRHybrid::numberOfFactors() const
{
    return numberOfFactors_;
}


const Vector& LMMSABRHybrid::resetTimes() const
{
    return resetTimes_;
}


const Vector& LMMSABRHybrid::accruals() const
{
    return accruals_;
}


const Vector& LMMSABRHybrid::initialForwards() const
{
    return initialForwards_;
}


const Vector&
LMMSABRHybrid::initialDiscountFactors() const
{
    return initialDiscountFactors_;
}


const SABRParameters&
LMMSABRHybrid::sabrParameters() const
{
    return sabrParameters_;
}


double LMMSABRHybrid::dotProduct(
    const Vector& first,
    const Vector& second
)
{
    if (first.size() != second.size())
    {
        throw std::invalid_argument(
            "Dot-product vectors have different sizes."
        );
    }

    double result = 0.0;

    for (std::size_t i = 0;
         i < first.size();
         ++i)
    {
        result += first[i] * second[i];
    }

    return result;
}


double LMMSABRHybrid::vectorNorm(
    const Vector& values
)
{
    return std::sqrt(
        dotProduct(
            values,
            values
        )
    );
}


void LMMSABRHybrid::validateModelInputs() const
{
    if (numberOfForwards_ == 0)
    {
        throw std::invalid_argument(
            "The model must contain forward rates."
        );
    }

    if (resetTimes_.size() !=
        numberOfForwards_)
    {
        throw std::invalid_argument(
            "resetTimes size must equal "
            "the number of forwards."
        );
    }

    if (accruals_.size() !=
        numberOfForwards_)
    {
        throw std::invalid_argument(
            "accruals size must equal "
            "the number of forwards."
        );
    }

    if (initialDiscountFactors_.size() !=
        numberOfForwards_ + 1)
    {
        throw std::invalid_argument(
            "initialDiscountFactors must contain "
            "one more value than initialForwards."
        );
    }

    if (correlationLoadings_.size() !=
        numberOfForwards_)
    {
        throw std::invalid_argument(
            "correlationLoadings must contain "
            "one row per forward."
        );
    }

    if (numberOfFactors_ == 0)
    {
        throw std::invalid_argument(
            "At least one rate factor is required."
        );
    }

    for (const Vector& row :
         correlationLoadings_)
    {
        if (row.size() !=
            numberOfFactors_)
        {
            throw std::invalid_argument(
                "All correlation-loading rows "
                "must have equal length."
            );
        }
    }

    if (sabrParameters_.numberOfForwards() !=
        numberOfForwards_)
    {
        throw std::invalid_argument(
            "SABR parameter dimension does not "
            "match the forward dimension."
        );
    }

    if (volatilityLevel_ < 0.0 ||
        volatilityDecay_ < 0.0 ||
        volatilityFloor_ < 0.0)
    {
        throw std::invalid_argument(
            "Volatility parameters must "
            "be non-negative."
        );
    }
}


Vector LMMSABRHybrid::activeMask(
    double time
) const
{
    Vector active(
        numberOfForwards_,
        0.0
    );

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        if (time <
            resetTimes_[i] - 1.0e-12)
        {
            active[i] = 1.0;
        }
    }

    return active;
}


Vector LMMSABRHybrid::deterministicVolatilities(
    double time
) const
{
    Vector volatilities(
        numberOfForwards_,
        0.0
    );

    Vector active =
        activeMask(
            time
        );

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        if (active[i] > 0.5)
        {
            double timeToReset =
                std::max(
                    resetTimes_[i] - time,
                    0.0
                );

            volatilities[i] =
                volatilityFloor_
                +
                volatilityLevel_
                *
                std::exp(
                    -volatilityDecay_
                    *
                    timeToReset
                );
        }
    }

    return volatilities;
}


Matrix LMMSABRHybrid::factorLoadings(
    double time,
    const Vector& forwards,
    const Vector& alpha
) const
{
    validateState(
        forwards,
        alpha
    );

    Vector deterministicVols =
        deterministicVolatilities(
            time
        );

    Vector active =
        activeMask(
            time
        );

    Matrix loadings(
        numberOfForwards_,
        Vector(
            numberOfFactors_,
            0.0
        )
    );

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        if (active[i] < 0.5)
        {
            continue;
        }

        double shiftedForward =
            forwards[i]
            +
            sabrParameters_.shift()[i];

        double cevTerm =
            std::pow(
                shiftedForward,
                sabrParameters_.beta()[i]
            );

        double volatilityScale =
            deterministicVols[i]
            *
            alpha[i]
            *
            cevTerm;

        for (std::size_t factor = 0;
             factor < numberOfFactors_;
             ++factor)
        {
            loadings[i][factor] =
                volatilityScale
                *
                correlationLoadings_[i][factor];
        }
    }

    return loadings;
}


Matrix LMMSABRHybrid::
instantaneousCovarianceMatrix(
    double time,
    const Vector& forwards,
    const Vector& alpha
) const
{
    Matrix loadings =
        factorLoadings(
            time,
            forwards,
            alpha
        );

    Matrix covariance(
        numberOfForwards_,
        Vector(
            numberOfForwards_,
            0.0
        )
    );

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        for (std::size_t j = 0;
             j < numberOfForwards_;
             ++j)
        {
            covariance[i][j] =
                dotProduct(
                    loadings[i],
                    loadings[j]
                );
        }
    }

    return covariance;
}


Vector LMMSABRHybrid::terminalMeasureDrift(
    double time,
    const Vector& forwards,
    const Vector& alpha
) const
{
    validateState(
        forwards,
        alpha
    );

    Matrix loadings =
        factorLoadings(
            time,
            forwards,
            alpha
        );

    Vector active =
        activeMask(
            time
        );

    Vector drift(
        numberOfForwards_,
        0.0
    );

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        if (active[i] < 0.5)
        {
            continue;
        }

        double total = 0.0;

        for (std::size_t j = i + 1;
             j < numberOfForwards_;
             ++j)
        {
            if (active[j] < 0.5)
            {
                continue;
            }

            double denominator =
                1.0
                +
                accruals_[j]
                *
                forwards[j];

            if (denominator <= 0.0)
            {
                throw std::runtime_error(
                    "Invalid LMM denominator: "
                    "1 + delta * L <= 0."
                );
            }

            double covariance =
                dotProduct(
                    loadings[i],
                    loadings[j]
                );

            total +=
                accruals_[j]
                *
                covariance
                /
                denominator;
        }

        drift[i] = -total;
    }

    return drift;
}


Vector LMMSABRHybrid::effectiveForwardShocks(
    double time,
    const Vector& forwards,
    const Vector& alpha,
    const Vector& rateFactorShocks
) const
{
    if (rateFactorShocks.size() !=
        numberOfFactors_)
    {
        throw std::invalid_argument(
            "Incorrect number of rate-factor shocks."
        );
    }

    Matrix loadings =
        factorLoadings(
            time,
            forwards,
            alpha
        );

    Vector shocks(
        numberOfForwards_,
        0.0
    );

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        double norm =
            vectorNorm(
                loadings[i]
            );

        if (norm > 1.0e-14)
        {
            shocks[i] =
                dotProduct(
                    loadings[i],
                    rateFactorShocks
                )
                /
                norm;
        }
    }

    return shocks;
}


void LMMSABRHybrid::evolve(
    double time,
    const Vector& forwards,
    const Vector& alpha,
    double dt,
    const Vector& rateFactorShocks,
    const Vector& independentVolatilityShocks,
    Vector& nextForwards,
    Vector& nextAlpha
) const
{
    if (dt <= 0.0)
    {
        throw std::invalid_argument(
            "The simulation time step must be positive."
        );
    }

    if (rateFactorShocks.size() !=
        numberOfFactors_)
    {
        throw std::invalid_argument(
            "Incorrect rate-factor shock dimension."
        );
    }

    if (independentVolatilityShocks.size() !=
        numberOfForwards_)
    {
        throw std::invalid_argument(
            "Incorrect volatility-shock dimension."
        );
    }

    validateState(
        forwards,
        alpha
    );

    Vector active =
        activeMask(
            time
        );

    Matrix loadings =
        factorLoadings(
            time,
            forwards,
            alpha
        );

    Vector drift =
        terminalMeasureDrift(
            time,
            forwards,
            alpha
        );

    Vector effectiveRateShocks =
        effectiveForwardShocks(
            time,
            forwards,
            alpha,
            rateFactorShocks
        );

    nextForwards = forwards;
    nextAlpha = alpha;

    double sqrtDt =
        std::sqrt(
            dt
        );

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        if (active[i] < 0.5)
        {
            continue;
        }

        double diffusion =
            dotProduct(
                loadings[i],
                rateFactorShocks
            )
            *
            sqrtDt;

        double proposedForward =
            forwards[i]
            +
            drift[i]
            *
            dt
            +
            diffusion;

        double minimumForward =
            -sabrParameters_.shift()[i]
            +
            1.0e-8;

        nextForwards[i] =
            std::max(
                proposedForward,
                minimumForward
            );

        double rho =
            sabrParameters_.rho()[i];

        double independentWeight =
            std::sqrt(
                std::max(
                    1.0 - rho * rho,
                    0.0
                )
            );

        double correlatedVolatilityShock =
            rho
            *
            effectiveRateShocks[i]
            +
            independentWeight
            *
            independentVolatilityShocks[i];

        double nu =
            sabrParameters_.nu()[i];

        double logIncrement =
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
            sqrtDt
            *
            correlatedVolatilityShock;

        double proposedAlpha =
            alpha[i]
            *
            std::exp(
                logIncrement
            );

        proposedAlpha =
            std::max(
                proposedAlpha,
                sabrParameters_.alphaFloor()
            );

        proposedAlpha =
            std::min(
                proposedAlpha,
                sabrParameters_.alphaCap()
            );

        nextAlpha[i] =
            proposedAlpha;
    }

    validateState(
        nextForwards,
        nextAlpha
    );
}


Vector LMMSABRHybrid::discountFactorsFromForwards(
    const Vector& forwards,
    std::size_t startIndex
) const
{
    if (forwards.size() !=
        numberOfForwards_)
    {
        throw std::invalid_argument(
            "Forward vector has incorrect size."
        );
    }

    if (startIndex >
        numberOfForwards_)
    {
        throw std::out_of_range(
            "Invalid discount-factor start index."
        );
    }

    Vector discountFactors(
        numberOfForwards_ + 1,
        std::numeric_limits<double>::quiet_NaN()
    );

    discountFactors[startIndex] = 1.0;

    for (std::size_t i = startIndex;
         i < numberOfForwards_;
         ++i)
    {
        double denominator =
            1.0
            +
            accruals_[i]
            *
            forwards[i];

        if (denominator <= 0.0)
        {
            throw std::runtime_error(
                "Cannot reconstruct discount factors: "
                "1 + delta * L <= 0."
            );
        }

        discountFactors[i + 1] =
            discountFactors[i]
            /
            denominator;
    }

    return discountFactors;
}


double LMMSABRHybrid::terminalBondFromForwards(
    const Vector& forwards,
    std::size_t startIndex
) const
{
    Vector discountFactors =
        discountFactorsFromForwards(
            forwards,
            startIndex
        );

    return discountFactors.back();
}


double LMMSABRHybrid::initialTerminalBond() const
{
    return initialDiscountFactors_.back();
}


void LMMSABRHybrid::validateState(
    const Vector& forwards,
    const Vector& alpha
) const
{
    if (forwards.size() !=
        numberOfForwards_)
    {
        throw std::invalid_argument(
            "Forward state has incorrect size."
        );
    }

    if (alpha.size() !=
        numberOfForwards_)
    {
        throw std::invalid_argument(
            "Alpha state has incorrect size."
        );
    }

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        if (!std::isfinite(forwards[i]) ||
            !std::isfinite(alpha[i]))
        {
            throw std::runtime_error(
                "The model state contains "
                "non-finite values."
            );
        }

        if (alpha[i] <= 0.0)
        {
            throw std::runtime_error(
                "Alpha must remain positive."
            );
        }

        if (forwards[i] +
            sabrParameters_.shift()[i]
            <= 0.0)
        {
            throw std::runtime_error(
                "Forward state violates "
                "L + shift > 0."
            );
        }

        if (1.0 +
            accruals_[i]
            *
            forwards[i]
            <= 0.0)
        {
            throw std::runtime_error(
                "Forward state violates "
                "1 + delta * L > 0."
            );
        }
    }
}


void LMMSABRHybrid::printSummary() const
{
    std::cout
        << "LMM-SABR Hybrid Model\n"
        << "------------------------------\n"
        << "Number of forwards: "
        << numberOfForwards_
        << "\n"
        << "Number of rate factors: "
        << numberOfFactors_
        << "\n"
        << "Volatility level: "
        << volatilityLevel_
        << "\n"
        << "Volatility decay: "
        << volatilityDecay_
        << "\n"
        << "Volatility floor: "
        << volatilityFloor_
        << "\n"
        << "Initial terminal bond: "
        << initialTerminalBond()
        << "\n";
}
