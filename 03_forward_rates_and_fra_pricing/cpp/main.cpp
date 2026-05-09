#include <iostream>
#include "curve.hpp"
#include "fra.hpp"

int main(){

    std::vector<double> mats =
    {1,2,5,10};

    std::vector<double> rates =
    {0.02,0.025,0.03,0.035};

    YieldCurve curve(
        mats,
        rates
    );

    FRA fra(
        1000000,
        0.025,
        1.0,
        1.5
    );

    std::cout
        << "FRA PV = "
        << fra.value(curve)
        << std::endl;

    return 0;
}
