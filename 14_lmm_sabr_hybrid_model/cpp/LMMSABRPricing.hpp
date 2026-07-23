#ifndef LMMSABRPRICING_HPP_INCLUDED
#define LMMSABRPRICING_HPP_INCLUDED


#include <cstddef>

#include "LMMSABRHybrid.hpp"
#include "SABRSimulation.hpp"


struct MonteCarloPriceResult
{
    double price;
    double standardError;
    double meanPayoff;
    std::size_t numberOfPaths;
};


Vector bondPricesFromForwards(
    const Vector& forwards,
    const Vector& accruals,
    std::size_t startForwardIndex
);


void swapAnnuityAndRate(
    const Vector& forwards,
    const Vector& accruals,
    std::size_t swapStartIndex,
    std::size_t swapEndIndex,
    double& annuity,
    double& swapRate
);


MonteCarloPriceResult priceCapletMC(
    const LMMSABRHybrid& model,
    const SABRSimulationResult& simulation,
    double resetTime,
    double strike,
    double notional
);


MonteCarloPriceResult pricePayerSwaptionMC(
    const LMMSABRHybrid& model,
    const SABRSimulationResult& simulation,
    double expiry,
    double swapEnd,
    double strike,
    double notional
);

#endif // LMMSABRPRICING_HPP_INCLUDED
