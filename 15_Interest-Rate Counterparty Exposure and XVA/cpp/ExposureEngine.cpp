#include "ExposureEngine.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>


std::size_t ForwardSimulationResult::numberOfPaths() const
{
    return forwardPaths.size();
}


std::size_t ForwardSimulationResult::numberOfTimes() const
{
    if (forwardPaths.empty())
    {
        return 0;
    }

    return forwardPaths.front().size();
}


std::size_t ForwardSimulationResult::numberOfForwards() const
{
    if (forwardPaths.empty() ||
        forwardPaths.front().empty())
    {
        return 0;
    }

    return forwardPaths
        .front()
        .front()
        .size();
}


std::size_t ExposureSimulationResult::numberOfPaths() const
{
    return portfolioValues.size();
}


std::size_t ExposureSimulationResult::numberOfTimes() const
{
    if (portfolioValues.empty())
    {
        return 0;
    }

    return portfolioValues.front().size();
}


std::size_t ExposureSimulationResult::numberOfTrades() const
{
    return tradeIds.size();
}


std::size_t exactTimeIndex(
    const Vector& times,
    double targetTime,
    double tolerance
)
{
    for (std::size_t index = 0;
         index < times.size();
         ++index)
    {
        if (std::fabs(
                times[index]
                -
                targetTime
            )
            <=
            tolerance)
        {
            return index;
        }
    }

    throw std::runtime_error(
        "Requested time is not present on the grid."
    );
}


Vector bondPricesFromForwards(
    const Vector& forwards,
    const Vector& accruals,
    std::size_t currentTenorIndex
)
{
    if (forwards.size() !=
        accruals.size())
    {
        throw std::invalid_argument(
            "forwards and accruals must have equal size."
        );
    }

    if (currentTenorIndex >
        forwards.size())
    {
        throw std::out_of_range(
            "Invalid currentTenorIndex."
        );
    }

    Vector bonds(
        forwards.size() + 1,
        std::numeric_limits<double>::quiet_NaN()
    );

    bonds[currentTenorIndex] = 1.0;

    for (std::size_t forwardIndex =
             currentTenorIndex;
         forwardIndex <
             forwards.size();
         ++forwardIndex)
    {
        double denominator =
            1.0
            +
            accruals[forwardIndex]
            *
            forwards[forwardIndex];

        if (denominator <= 0.0)
        {
            throw std::runtime_error(
                "Invalid forward curve: "
                "1 + delta * L must remain positive."
            );
        }

        bonds[forwardIndex + 1] =
            bonds[forwardIndex]
            /
            denominator;
    }

    return bonds;
}


double valueInterestRateSwap(
    const InterestRateSwap& trade,
    double valuationTime,
    const Vector& forwards,
    const Vector& tenorTimes,
    const Vector& accruals
)
{
    if (valuationTime >=
        trade.endTime())
    {
        return 0.0;
    }

    std::size_t currentIndex =
        exactTimeIndex(
            tenorTimes,
            valuationTime
        );

    std::size_t swapStartIndex =
        exactTimeIndex(
            tenorTimes,
            trade.startTime()
        );

    std::size_t swapEndIndex =
        exactTimeIndex(
            tenorTimes,
            trade.endTime()
        );

    std::size_t effectiveStartIndex =
        std::max(
            currentIndex,
            swapStartIndex
        );

    Vector bonds =
        bondPricesFromForwards(
            forwards,
            accruals,
            currentIndex
        );

    double startBond =
        bonds[effectiveStartIndex];

    double endBond =
        bonds[swapEndIndex];

    if (!std::isfinite(startBond) ||
        !std::isfinite(endBond))
    {
        throw std::runtime_error(
            "Required bond price is unavailable."
        );
    }

    double floatingLeg =
        startBond
        -
        endBond;

    double fixedLegAnnuity =
        0.0;

    for (std::size_t paymentIndex =
             effectiveStartIndex;
         paymentIndex <
             swapEndIndex;
         ++paymentIndex)
    {
        fixedLegAnnuity +=
            accruals[paymentIndex]
            *
            bonds[paymentIndex + 1];
    }

    double fixedLeg =
        trade.fixedRate()
        *
        fixedLegAnnuity;

    double payerFixedValue =
        trade.notional()
        *
        (
            floatingLeg
            -
            fixedLeg
        );

    return
        trade.direction()
        *
        payerFixedValue;
}


Vector buildExposureTimes(
    const Vector& tenorTimes,
    const Vector& simulationTimes,
    double finalTime,
    double tolerance
)
{
    Vector exposureTimes;

    for (double tenorTime :
         tenorTimes)
    {
        if (tenorTime >
            finalTime + tolerance)
        {
            continue;
        }

        bool found = false;

        for (double simulationTime :
             simulationTimes)
        {
            if (std::fabs(
                    tenorTime
                    -
                    simulationTime
                )
                <=
                tolerance)
            {
                found = true;
                break;
            }
        }

        if (found)
        {
            exposureTimes.push_back(
                tenorTime
            );
        }
    }

    if (exposureTimes.empty())
    {
        throw std::runtime_error(
            "No common exposure times were found."
        );
    }

    return exposureTimes;
}


ExposureSimulationResult simulatePortfolioValues(
    const Vector& tenorTimes,
    const Vector& accruals,
    const ForwardSimulationResult& simulation,
    const NettingSet& nettingSet,
    const Vector& exposureTimes
)
{
    if (tenorTimes.size() !=
        accruals.size() + 1)
    {
        throw std::invalid_argument(
            "tenorTimes must contain one more "
            "element than accruals."
        );
    }

    std::size_t numberOfPaths =
        simulation.numberOfPaths();

    std::size_t numberOfExposureTimes =
        exposureTimes.size();

    std::size_t numberOfTrades =
        nettingSet.numberOfTrades();

    ExposureSimulationResult result;

    result.exposureTimes =
        exposureTimes;

    for (const InterestRateSwap& trade :
         nettingSet.trades())
    {
        result.tradeIds.push_back(
            trade.tradeId()
        );
    }

    result.tradeValues =
        Tensor3D(
            numberOfPaths,
            std::vector<Vector>(
                numberOfExposureTimes,
                Vector(
                    numberOfTrades,
                    0.0
                )
            )
        );

    result.portfolioValues =
        Matrix(
            numberOfPaths,
            Vector(
                numberOfExposureTimes,
                0.0
            )
        );

    for (std::size_t timePosition = 0;
         timePosition <
             numberOfExposureTimes;
         ++timePosition)
    {
        double exposureTime =
            exposureTimes[timePosition];

        std::size_t simulationTimeIndex =
            exactTimeIndex(
                simulation.times,
                exposureTime
            );

        for (std::size_t pathIndex = 0;
             pathIndex <
                 numberOfPaths;
             ++pathIndex)
        {
            const Vector& forwards =
                simulation
                    .forwardPaths
                    [pathIndex]
                    [simulationTimeIndex];

            double portfolioValue =
                0.0;

            for (std::size_t tradeIndex = 0;
                 tradeIndex <
                     numberOfTrades;
                 ++tradeIndex)
            {
                double tradeValue =
                    valueInterestRateSwap(
                        nettingSet
                            .trades()
                            [tradeIndex],
                        exposureTime,
                        forwards,
                        tenorTimes,
                        accruals
                    );

                result
                    .tradeValues
                    [pathIndex]
                    [timePosition]
                    [tradeIndex]
                    =
                    tradeValue;

                portfolioValue +=
                    tradeValue;
            }

            result
                .portfolioValues
                [pathIndex]
                [timePosition]
                =
                portfolioValue;
        }
    }

    return result;
}
