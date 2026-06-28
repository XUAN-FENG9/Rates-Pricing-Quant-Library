#include <iostream>
#include <vector>
#include <iomanip>

#include "curve.hpp"
#include "HullWhiteModel.hpp"

#include "BermudanSwaption.hpp"
#include "HullWhiteTree.hpp"
#include "TreePricer.hpp"

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
        2. Hull-White baseline model.
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

        Exercise:
            1Y, 2Y, 3Y, 4Y, 5Y

        Each exercise enters a 5Y swap.
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

    std::cout
        << "\nExercise dates:"
        << std::endl;

    for(double t : bermudan.exerciseDates){

        std::cout
            << t
            << " ";
    }

    std::cout
        << std::endl;

    /*
        4. Build short-rate tree.
    */

    HullWhiteBinomialTree tree(
        &hwModel,
        5.0,
        40,
        r0
    );

    std::cout
        << "\nTree summary"
        << std::endl;

    std::cout
        << "dt      = "
        << tree.dt
        << std::endl;

    std::cout
        << "deltaR  = "
        << tree.deltaR
        << std::endl;

    std::cout
        << "final min rate = "
        << tree.rates.back().front()
        << std::endl;

    std::cout
        << "final max rate = "
        << tree.rates.back().back()
        << std::endl;

    /*
        5. Price Bermudan swaption.
    */

    BermudanSwaptionTreePricer pricer(
        &tree,
        &bermudan
    );

    double price =
        pricer.price();

    std::cout
        << "\nBermudan swaption price: "
        << price
        << std::endl;

    /*
        6. Inspect root node values.
    */

    std::cout
        << "\nRoot node diagnostics"
        << std::endl;

    std::cout
        << "Value tree root: "
        << pricer.valueTree[0][0]
        << std::endl;

    std::cout
        << "Continuation root: "
        << pricer.continuationValueTree[0][0]
        << std::endl;

    std::cout
        << "Exercise root: "
        << pricer.exerciseValueTree[0][0]
        << std::endl;

    std::cout
        << "Exercise flag root: "
        << pricer.exerciseFlagTree[0][0]
        << std::endl;

    /*
        7. Print exercise nodes by step.
    */

    std::cout
        << "\nExercise statistics:"
        << std::endl;

    for(int step = 0; step <= tree.nSteps; ++step){

        int count =
            0;

        for(bool flag : pricer.exerciseFlagTree[step]){

            if(flag){
                count++;
            }
        }

        if(count > 0){

            std::cout
                << "time="
                << tree.times[step]
                << ", exercise nodes="
                << count
                << " / "
                << pricer.exerciseFlagTree[step].size()
                << std::endl;
        }
    }

    /*
        8. Fixed-rate sensitivity.
    */

    std::cout
        << "\nFixed-rate sensitivity:"
        << std::endl;

    std::vector<double> fixedRates = {
        0.035,
        0.040,
        0.045,
        0.050,
        0.055
    };

    for(double K : fixedRates){

        BermudanSwaption inst(
            1000000.0,
            K,
            1.0,
            5.0,
            5.0,
            2,
            1,
            true
        );

        BermudanSwaptionTreePricer p(
            &tree,
            &inst
        );

        double px =
            p.price();

        std::cout
            << "K="
            << K
            << ", price="
            << px
            << std::endl;
    }

    return 0;
}
