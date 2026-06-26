#include "curve.hpp"
#include <cmath>

YieldCurve::YieldCurve(
    const std::vector<double>& mats,
    const std::vector<double>& rates
){

    maturities = mats;
    zero_rates = rates;
}

double YieldCurve::zero_rate(double t){

    for(size_t i=1;i<maturities.size();++i){

        if(t <= maturities[i]){

            double t1 = maturities[i-1];
            double t2 = maturities[i];

            double r1 = zero_rates[i-1];
            double r2 = zero_rates[i];

            double w =
                (t-t1)/(t2-t1);

            return r1 + w*(r2-r1);
        }
    }

    return zero_rates.back();
}

double YieldCurve::discount_factor(double t){

    double r = zero_rate(t);

    return exp(-r*t);
}

double YieldCurve::forward_rate(
    double t1,
    double t2
){

    double df1 =
        discount_factor(t1);

    double df2 =
        discount_factor(t2);

    return
        ((df1/df2)-1.0)/(t2-t1);
}
