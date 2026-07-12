#ifndef DIAGNOSTICS_HPP_INCLUDED
#define DIAGNOSTICS_HPP_INCLUDED

#include "GaussianLMM.hpp"
#include "LMMSimulation.hpp"

/*
    Diagnostics.hpp

    Console diagnostics for the Gaussian LMM demonstration.
*/

void printForwardCurve(
    const GaussianLMM& model
);

void printCorrelationSummary(
    const Matrix& correlationMatrix
);

void printSimulationSummary(
    const GaussianLMM& model,
    const LMMSimulationResult& simulation
);

void printPricingSummary(
    double capletPrice,
    double swaptionPrice
);

#endif // DIAGNOSTICS_HPP_INCLUDED
