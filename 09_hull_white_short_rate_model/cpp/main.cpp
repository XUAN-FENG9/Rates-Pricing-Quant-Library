#include <iostream>
#include <vector>
#include <iomanip>

#include "curve.hpp"

#include "HullWhiteModel.hpp"
#include "BondPricing.hpp"
#include "HullWhiteSimulation.hpp"
#include "BondOptionPricing.hpp"

int main(){

    /*
        1. Build yield curve.

        Same curve as previous chapters.
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
        2. Create Hull-White model.
    */

    double meanReversion = 0.05;
    double volatility = 0.01;

    HullWhiteModel model(
        meanReversion,
        volatility,
        &curve
    );

    std::cout
        << std::fixed
        << std::setprecision(8);

    double r0 =
        model.instantaneousForwardRate(
            1e-6
        );

    std::cout
        << "Initial short-rate proxy: "
        << r0
        << std::endl;

    std::cout
        << "Theta(2Y): "
        << model.theta(2.0)
        << std::endl;

    /*
        3. Check B(0,T).
    */

    std::cout
        << "\nB(0,T) values:"
        << std::endl;

    for(double T : {1.0, 2.0, 5.0, 10.0, 30.0}){

        std::cout
            << "B(0,"
            << T
            << ") = "
            << model.B(0.0, T)
            << std::endl;
    }

    /*
        4. Zero-coupon bond pricing.
    */

    double t = 2.0;
    double T = 10.0;
    double r_t = 0.04;

    double bondPrice =
        zeroCouponBondPrice(
            model,
            t,
            T,
            r_t
        );

    std::cout
        << "\nP("
        << t
        << ","
        << T
        << ") = "
        << bondPrice
        << std::endl;

    /*
        5. Simulate short-rate paths.
    */

    SimulationResult sim =
        simulateShortRatePaths(
            model,
            r0,
            10.0,
            240,
            5000,
            42
        );

    double mcDF =
        monteCarloZeroCouponBondPrice(
            sim
        );

    double marketDF =
        curve.discount_factor(10.0);

    std::cout
        << "\nMarket 10Y DF: "
        << marketDF
        << std::endl;

    std::cout
        << "MC 10Y DF    : "
        << mcDF
        << std::endl;

    std::cout
        << "Difference   : "
        << mcDF - marketDF
        << std::endl;

    /*
        6. Analytic zero-coupon bond option.
    */

    double optionExpiry = 2.0;
    double bondMaturity = 10.0;
    double strike = 0.75;

    double analyticPrice =
        priceZeroCouponBondOption(
            model,
            optionExpiry,
            bondMaturity,
            strike,
            true
        );

    std::cout
        << "\nAnalytic bond call price: "
        << analyticPrice
        << std::endl;

    /*
        7. Monte Carlo bond option price.
    */

    SimulationResult optionSim =
        simulateShortRatePaths(
            model,
            r0,
            optionExpiry,
            120,
            20000,
            123
        );

    double mcOptionPrice =
        monteCarloBondOptionPrice(
            model,
            optionSim,
            optionExpiry,
            bondMaturity,
            strike,
            true
        );

    std::cout
        << "MC bond call price      : "
        << mcOptionPrice
        << std::endl;

    std::cout
        << "Difference              : "
        << mcOptionPrice - analyticPrice
        << std::endl;

    return 0;
}
