#include "forward_swap.hpp"

ForwardStartingSwap::ForwardStartingSwap(
    double N,
    //double K,
    double start_time,
    double end_time,
    int freq
){

    notional = N;

    //fixed_rate = K;

    start = start_time;

    end = end_time;

    frequency = freq;

    double step =
        1.0 / frequency;

    double t =
        start + step;

    while(t <= end + 1e-10){

        payment_dates.push_back(t);

        t += step;
    }
}

double ForwardStartingSwap::annuity(
    YieldCurve& curve
){

    double A = 0.0;

    double previous = start;

    for(double t : payment_dates){

        double accrual =
            t - previous;

        double df =
            curve.discount_factor(t);

        A += accrual * df;

        previous = t;
    }

    return A;
}

double ForwardStartingSwap::forward_swap_rate(
    YieldCurve& curve
){

    double P0 =
        curve.discount_factor(start);

    double Pn =
        curve.discount_factor(end);

    double A =
        annuity(curve);

    return (P0 - Pn) / A;
}
