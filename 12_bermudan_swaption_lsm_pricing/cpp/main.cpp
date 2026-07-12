#include <iostream>
#include <vector>
#include <iomanip>

#include "../../06_black_swaption_pricing/cpp/curve.hpp"
#include "../../09_hull_white_short_rate_model/cpp/HullWhiteModel.hpp"

#include "../../11_bermudan_swaption_tree_pricing/cpp/BermudanSwaption.hpp"
#include "../../11_bermudan_swaption_tree_pricing/cpp/HullWhiteTree.hpp"
#include "../../11_bermudan_swaption_tree_pricing/cpp/TreePricer.hpp"

#include "LSMPathSimulation.hpp"
#include "LSMBermudanPricer.hpp"

int main(){

    std::cout
        << std::fixed
        << std::setprecision(8);

    /*
        1. Build yield curve.
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
        2. Hull-White model.
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
        3. Bermudan swaption.
    */

    BermudanSwaption bermudan(
        1000000.0,
        0.045,
        1.0,
        5.0,
        5.0,
        2,
        1,
        true
    );

    /*
        4. Simulate Hull-White paths.
    */

    LSMPathSimulationResult sim =
        simulateHullWhitePathsForLSM(
            hwModel,
            r0,
            10.0,
            200,
            20000,
            42
        );

    std::cout
        << "Number of paths: "
        << sim.ratePaths.size()
        << std::endl;

    /*
        5. LSM price.
    */

    LSMBermudanPricer lsmPricer(
        &hwModel,
        &bermudan,
        sim.times,
        sim.ratePaths,
        "rate_swap",
        2
    );

    double lsmPrice =
        lsmPricer.price();

    std::cout
        << "\nLSM Bermudan price: "
        << lsmPrice
        << std::endl;

    lsmPricer.printExerciseSummary();

    lsmPricer.printRegressionDiagnostics();

    /*
        6. Compare with Chapter 11 tree price.
    */

    HullWhiteBinomialTree tree(
        &hwModel,
        5.0,
        80,
        r0
    );

    BermudanSwaptionTreePricer treePricer(
        &tree,
        &bermudan
    );

    double treePrice =
        treePricer.price();

    std::cout
        << "\nTree price: "
        << treePrice
        << std::endl;

    std::cout
        << "LSM price : "
        << lsmPrice
        << std::endl;

    std::cout
        << "Difference: "
        << lsmPrice - treePrice
        << std::endl;

    /*
        7. Basis sensitivity.
    */

    std::cout
        << "\nBasis sensitivity:"
        << std::endl;

    std::vector<std::string> basisTypes = {
        "rate",
        "swap",
        "rate_swap"
    };

    for(const auto& basis : basisTypes){

        LSMBermudanPricer p(
            &hwModel,
            &bermudan,
            sim.times,
            sim.ratePaths,
            basis,
            2
        );

        double px =
            p.price();

        std::cout
            << basis
            << ": "
            << px
            << std::endl;
    }

    return 0;
}
