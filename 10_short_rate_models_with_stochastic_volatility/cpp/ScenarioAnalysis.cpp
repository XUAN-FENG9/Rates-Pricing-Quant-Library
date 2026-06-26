#include "ScenarioAnalysis.hpp"

#include <cmath>
#include <iomanip>

/*
    Helper function for mean.
*/

double mean(
    const std::vector<double>& x
){

    double sum =
        0.0;

    for(double v : x){

        sum += v;
    }

    return
        sum
        /
        static_cast<double>(
            x.size()
        );
}

/*
    Helper function for standard deviation.
*/

double stddev(
    const std::vector<double>& x
){

    double m =
        mean(x);

    double sum =
        0.0;

    for(double v : x){

        double diff =
            v - m;

        sum +=
            diff
            *
            diff;
    }

    return
        std::sqrt(
            sum
            /
            static_cast<double>(
                x.size()
            )
        );
}

/*
    Run one stochastic-vol scenario.
*/

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
    unsigned int seed
){

    StochasticVolModel model(
        baseModel,
        kappa,
        vBar,
        eta,
        rho
    );

    StochasticVolSimulationResult sim =
        simulateStochasticVolPaths(
            model,
            r0,
            vBar,
            maturity,
            nSteps,
            nPaths,
            seed
        );

    double bondPrice =
        monteCarloZeroCouponBondPrice(
            sim,
            bondMaturity
        );

    double optionPrice =
        monteCarloBondOptionPrice(
            sim,
            optionExpiry,
            optionBondMaturity,
            optionStrike,
            true
        );

    std::vector<double> finalRates;
    std::vector<double> finalVols;

    for(size_t p = 0; p < sim.ratePaths.size(); ++p){

        finalRates.push_back(
            sim.ratePaths[p].back()
        );

        finalVols.push_back(
            std::sqrt(
                sim.variancePaths[p].back()
            )
        );
    }

    ScenarioResult result;

    result.kappa = kappa;
    result.vBar = vBar;
    result.eta = eta;
    result.rho = rho;

    result.bondPrice = bondPrice;
    result.bondOptionPrice = optionPrice;

    result.terminalRateMean = mean(finalRates);
    result.terminalRateStd = stddev(finalRates);

    result.terminalVolMean = mean(finalVols);
    result.terminalVolStd = stddev(finalVols);

    return result;
}

/*
    Eta scenario set.
*/

std::vector<ScenarioResult> runEtaScenarios(
    HullWhiteModel* baseModel,
    double r0,
    const std::vector<double>& etaValues
){

    std::vector<ScenarioResult> results;

    for(double eta : etaValues){

        results.push_back(
            runSingleScenario(
                baseModel,
                r0,
                1.0,        // kappa
                0.0001,     // vBar
                eta,
                -0.30,      // rho
                10.0,
                240,
                5000,
                5.0,
                2.0,
                5.0,
                0.90,
                42
            )
        );
    }

    return results;
}

/*
    Rho scenario set.
*/

std::vector<ScenarioResult> runRhoScenarios(
    HullWhiteModel* baseModel,
    double r0,
    const std::vector<double>& rhoValues
){

    std::vector<ScenarioResult> results;

    for(double rho : rhoValues){

        results.push_back(
            runSingleScenario(
                baseModel,
                r0,
                1.0,
                0.0001,
                0.20,
                rho,
                10.0,
                240,
                5000,
                5.0,
                2.0,
                5.0,
                0.90,
                42
            )
        );
    }

    return results;
}

/*
    Kappa scenario set.
*/

std::vector<ScenarioResult> runKappaScenarios(
    HullWhiteModel* baseModel,
    double r0,
    const std::vector<double>& kappaValues
){

    std::vector<ScenarioResult> results;

    for(double kappa : kappaValues){

        results.push_back(
            runSingleScenario(
                baseModel,
                r0,
                kappa,
                0.0001,
                0.20,
                -0.30,
                10.0,
                240,
                5000,
                5.0,
                2.0,
                5.0,
                0.90,
                42
            )
        );
    }

    return results;
}

/*
    Print scenario table.
*/

void printScenarioTable(
    const std::vector<ScenarioResult>& results,
    const std::string& title
){

    std::cout
        << "\n"
        << title
        << std::endl;

    std::cout
        << "================================================================================"
        << std::endl;

    std::cout
        << std::setw(8) << "kappa"
        << std::setw(10) << "vBar"
        << std::setw(8) << "eta"
        << std::setw(8) << "rho"
        << std::setw(14) << "bond"
        << std::setw(14) << "option"
        << std::setw(14) << "rateStd"
        << std::setw(14) << "volMean"
        << std::endl;

    for(const auto& r : results){

        std::cout
            << std::setw(8) << r.kappa
            << std::setw(10) << r.vBar
            << std::setw(8) << r.eta
            << std::setw(8) << r.rho
            << std::setw(14) << r.bondPrice
            << std::setw(14) << r.bondOptionPrice
            << std::setw(14) << r.terminalRateStd
            << std::setw(14) << r.terminalVolMean
            << std::endl;
    }
}
