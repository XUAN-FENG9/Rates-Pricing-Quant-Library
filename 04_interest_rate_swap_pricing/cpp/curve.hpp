#ifndef CURVE_HPP_INCLUDED
#define CURVE_HPP_INCLUDED

#include <vector>

class YieldCurve {

public:

    std::vector<double> maturities;
    std::vector<double> zero_rates;

    YieldCurve(
        const std::vector<double>& mats,
        const std::vector<double>& rates
    );

    double zero_rate(double t);

    double discount_factor(double t);

    double forward_rate(
        double t1,
        double t2
    );
};


#endif // CURVE_HPP_INCLUDED
