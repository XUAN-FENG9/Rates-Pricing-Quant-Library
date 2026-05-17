#include <iostream>

#include "curve.hpp"
#include "swap.hpp"
#include "risk.hpp"

int main(){

    std::vector<double> mats =
    {1,2,5,10};

    std::vector<double> rates =
    {0.02,0.025,0.03,0.035};

    YieldCurve curve(
        mats,
        rates
    );

    InterestRateSwap swap(
        10000000,
        0.03,
        5.0
    );

    double risk =
        dv01(
            swap,
            curve
        );

    std::cout
        << "DV01 = "
        << risk
        << std::endl;

    return 0;
}
