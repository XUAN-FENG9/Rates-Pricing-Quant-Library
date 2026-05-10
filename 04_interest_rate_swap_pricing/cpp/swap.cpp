#include "swap.hpp"
#include <iostream>

InterestRateSwap::InterestRateSwap(
    double N,
    double K,
    double T
){

    notional = N;
    fixed_rate = K;
    maturity = T;

    // ------------------------------------------------
    // Generate semiannual payment schedule
    // ------------------------------------------------

    int frequency = 2;

    int n_payments =
        static_cast<int>(
            maturity * frequency
        );

    for(int i=1;
        i<=n_payments;
        ++i){

        double t =
            static_cast<double>(i)
            / frequency;

        payment_dates.push_back(t);
    }
}

double InterestRateSwap::npv(
    YieldCurve& curve
){

    double fixed_pv = 0.0;
    double float_pv = 0.0;

    double previous = 0.0;

    for(double t : payment_dates){

        double accrual =
            t - previous;

        double fwd =
            curve.forward_rate(
                previous,
                t
            );

        double df =
            curve.discount_factor(t);

        fixed_pv +=
            notional
            * fixed_rate
            * accrual
            * df;

        float_pv +=
            notional
            * fwd
            * accrual
            * df;

        previous = t;
    }

    std::cout
        << "Final Fixed Leg PV = "
        << fixed_pv
        << std::endl;

    std::cout
        << "Final Floating Leg PV = "
        << float_pv
        << std::endl;

    return float_pv - fixed_pv;
}
