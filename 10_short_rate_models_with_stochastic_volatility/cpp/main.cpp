#include <iostream>
#include <vector>
#include <iomanip>

#include "curve.hpp"
#include "HullWhiteModel.hpp"
#include "HullWhiteSimulation.hpp"
#include "BondOptionPricing.hpp"

#include "StochasticVolModel.hpp"
#include "StochasticVolSimulation.hpp"
#include "StochasticVolPricing.hpp"
#include "ScenarioAnalysis.hpp"

int main(){

    std::cout
        << std::fixed
        << std::setprecision(8);

    /*
        1. Build curve.
    */

    std::vector<double> maturities = {
        0.0833, 0.1667, 0.25, 0.5, 0.75,
        1.0, 1.5, 2.0, 2.5, 3.0,
        3.5, 4.0, 4.5, 5.0, 6.0,
        7.0, 8.0, 9.0, 10.0, 12.0,
        15.0, 20.0, 25.0, 30.0
    };

    std::vector<double> zeroRates = {
        0.0452, 0.0453, 0.0454, 0.0456, 0.0457,
        0.0458, 0.0459, 0.0458, 0.0457, 0.0455,
        0.0453, 0.0451, 0.0449, 0.0447, 0.0444,
        0.0441, 0.0439, 0.0437, 0.0435, 0.0432,
        0.0429, 0.0426, 0.0424, 0.0422

    };

    YieldCurve curve(
        maturities,
        zeroRates
    );

    /*
        2. Build Chapter 09 Hull-White baseline.
    */

    HullWhiteModel hwModel(
        0.05,
        0.01,
        &curve
    );

    double r0 =
        hwModel.instantaneousForwardRate(
            1e-6
        );

    std::cout
        << "Initial short-rate proxy: "
        << r0
        << std::endl;

    /*
        3. Build stochastic-vol model.
    */

    StochasticVolModel svModel(
        &hwModel,
        1.0,        // kappa
        0.0001,     // vBar
        0.20,       // eta
        -0.30       // rho
    );

    /*
        4. Simulate stochastic-vol paths.
    */

    StochasticVolSimulationResult svSim =
        simulateStochasticVolPaths(
            svModel,
            r0,
            0.0001,
            10.0,
            240,
            5000,
            42
        );

    double svBondPrice =
        monteCarloZeroCouponBondPrice(
            svSim,
            5.0
        );

    double svOptionPrice =
        monteCarloBondOptionPrice(
            svSim,
            2.0,
            5.0,
            0.90,
            true
        );

    std::cout
        << "\nStochastic-Vol 5Y Bond Price: "
        << svBondPrice
        << std::endl;

    std::cout
        << "Stochastic-Vol Bond Option Price: "
        << svOptionPrice
        << std::endl;

    /*
        5. Compare with constant-vol Hull-White bond option.
    */

    double hwOptionPrice =
        priceZeroCouponBondOption(
            hwModel,
            2.0,
            5.0,
            0.90,
            true
        );

    std::cout
        << "Constant-Vol Hull-White Option Price: "
        << hwOptionPrice
        << std::endl;

    std::cout
        << "SV - HW Option Difference: "
        << svOptionPrice - hwOptionPrice
        << std::endl;

    /*
        6. Scenario analysis.
    */

    std::vector<double> etaValues = {
        0.05,
        0.10,
        0.20,
        0.40,
        0.80
    };

    std::vector<double> rhoValues = {
        -0.80,
        -0.50,
        -0.30,
        0.00,
        0.30,
        0.50
    };

    std::vector<double> kappaValues = {
        0.20,
        0.50,
        1.00,
        2.00,
        4.00
    };

    printScenarioTable(
        runEtaScenarios(
            &hwModel,
            r0,
            etaValues
        ),
        "Eta Scenario Analysis"
    );

    printScenarioTable(
        runRhoScenarios(
            &hwModel,
            r0,
            rhoValues
        ),
        "Rho Scenario Analysis"
    );

    printScenarioTable(
        runKappaScenarios(
            &hwModel,
            r0,
            kappaValues
        ),
        "Kappa Scenario Analysis"
    );

    return 0;
}
