#ifndef EXPOSUREENGINE_H_INCLUDED
#define EXPOSUREENGINE_H_INCLUDED


#include <cstddef>
#include <string>
#include <vector>

#include "InterestRateTrade.hpp"
#include "XVAData.hpp"


struct ForwardSimulationResult
{
    Vector times;

    Tensor3D forwardPaths;

    std::size_t numberOfPaths() const;

    std::size_t numberOfTimes() const;

    std::size_t numberOfForwards() const;
};


struct ExposureSimulationResult
{
    Vector exposureTimes;

    std::vector<std::string> tradeIds;

    Tensor3D tradeValues;

    Matrix portfolioValues;

    std::size_t numberOfPaths() const;

    std::size_t numberOfTimes() const;

    std::size_t numberOfTrades() const;
};


std::size_t exactTimeIndex(
    const Vector& times,
    double targetTime,
    double tolerance = 1.0e-10
);


Vector bondPricesFromForwards(
    const Vector& forwards,
    const Vector& accruals,
    std::size_t currentTenorIndex
);


double valueInterestRateSwap(
    const InterestRateSwap& trade,
    double valuationTime,
    const Vector& forwards,
    const Vector& tenorTimes,
    const Vector& accruals
);


Vector buildExposureTimes(
    const Vector& tenorTimes,
    const Vector& simulationTimes,
    double finalTime,
    double tolerance = 1.0e-10
);


ExposureSimulationResult simulatePortfolioValues(
    const Vector& tenorTimes,
    const Vector& accruals,
    const ForwardSimulationResult& simulation,
    const NettingSet& nettingSet,
    const Vector& exposureTimes
);

#endif // EXPOSUREENGINE_H_INCLUDED
