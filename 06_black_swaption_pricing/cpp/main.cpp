#include <iostream>

#include "curve.hpp"
#include "forward_swap.hpp"
#include "black_swaption.hpp"
#include "bachelier_swaption.hpp"


int main(){

    std::vector<double> mats =
    {1,2,5,10};

    std::vector<double> rates =
    {0.02,0.025,0.03,0.035};

    YieldCurve curve(
        mats,
        rates
    );

    ForwardStartingSwap swap(
        10000000,
        //0.03,
        1.0,
        6.0,
        2
    );

    BlackSwaption black_swaption(
        10'000'000,
        0.03,
        swap.start,
        0.10,
        swap,
        true
    );

    double black_price =
        black_swaption.price(curve);

    std::cout
        << "BlackSwaption Price = "
        << black_price
        << std::endl;

    BachelierSwaption bachelier_swaption(
        10'000'000,
        0.03,
        swap.start,
        0.10,
        swap,
        true
    );

    double bachelier_price =
        bachelier_swaption.price(curve);

    std::cout
        << "BachelierSwaption Price = "
        << bachelier_price
        << std::endl;

    return 0;
}
