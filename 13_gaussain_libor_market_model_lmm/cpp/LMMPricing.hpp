#ifndef LMMPRICING_HPP_INCLUDED
#define LMMPRICING_HPP_INCLUDED

#include <vector>

#include "GaussianLMM.hpp"
#include "LMMSimulation.hpp"

/*
    LMMPricing.hpp

    Terminal-measure Monte Carlo pricing.
*/

struct SwapState {

    double annuity;
    double swapRate;
};

std::vector<double> bondPricesFromForwards(
    const std::vector<double>& forwards,
    const TenorStructure& tenor,
    int startForwardIndex
);

SwapState swapAnnuityAndRate(
    const std::vector<double>& forwards,
    const TenorStructure& tenor,
    int swapStartIndex,
    int swapEndIndex
);

double priceCapletMonteCarlo(
    const GaussianLMM& model,
    const LMMSimulationResult& simulation,
    double resetTime,
    double strike,
    double notional = 1000000.0
);

double pricePayerSwaptionMonteCarlo(
    const GaussianLMM& model,
    const LMMSimulationResult& simulation,
    double expiry,
    double swapEnd,
    double strike,
    double notional = 1000000.0
);

#endif // LMMPRICING_HPP_INCLUDED
