#ifndef SCENARIOANALYSIS_HPP_INCLUDED
#define SCENARIOANALYSIS_HPP_INCLUDED

#include <vector>
#include <iostream>

#include "StochasticVolModel.hpp"
#include "StochasticVolSimulation.hpp"
#include "StochasticVolPricing.hpp"

/*
    Scenario result container.
*/

struct ScenarioResult {

    double kappa;
    double vBar;
    double eta;
    double rho;

    double bondPrice;
    double bondOptionPrice;

    double terminalRateMean;
    double terminalRateStd;

    double terminalVolMean;
    double terminalVolStd;
};

ScenarioResult runSingleScenario(
    HullWhiteModel* baseModel,
    double r0,
    double kappa,
    double vBar,
    double eta,
    double rho,
    double maturity,
    int nSteps,
    int nPaths,
    double bondMaturity,
    double optionExpiry,
    double optionBondMaturity,
    double optionStrike,
    unsigned int seed = 42
);

std::vector<ScenarioResult> runEtaScenarios(
    HullWhiteModel* baseModel,
    double r0,
    const std::vector<double>& etaValues
);

std::vector<ScenarioResult> runRhoScenarios(
    HullWhiteModel* baseModel,
    double r0,
    const std::vector<double>& rhoValues
);

std::vector<ScenarioResult> runKappaScenarios(
    HullWhiteModel* baseModel,
    double r0,
    const std::vector<double>& kappaValues
);

void printScenarioTable(
    const std::vector<ScenarioResult>& results,
    const std::string& title
);

#endif // SCENARIOANALYSIS_HPP_INCLUDED
