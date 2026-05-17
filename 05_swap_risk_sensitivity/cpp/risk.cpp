#include "risk.hpp"

double dv01(
    InterestRateSwap& swap,
    YieldCurve& curve
){

    double base_npv =
        swap.npv(curve);

    std::vector<double> bumped_rates =
        curve.zero_rates;

    for(double& r : bumped_rates){

        r += 0.0001;
    }

    YieldCurve bumped_curve(
        curve.maturities,
        bumped_rates
    );

    double bumped_npv =
        swap.npv(bumped_curve);

    return bumped_npv
        - base_npv;
}
