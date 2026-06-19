#include "BondPricing.hpp"

#include <cmath>
#include <stdexcept>

/*
    Hull-White A(t,T).

    A(t,T) ensures exact fit to the initial curve.
*/

double AFunction(
    const HullWhiteModel& model,
    double t,
    double T
){

    if(T < t){
        throw std::runtime_error(
            "T must be greater than or equal to t."
        );
    }

    double P0T =
        model.curve->discount_factor(T);

    double P0t =
        model.curve->discount_factor(t);

    double B =
        model.B(t, T);

    double f0t =
        model.instantaneousForwardRate(t);

    double a =
        model.a;

    double sigma =
        model.sigma;

    double varianceAdjustment;

    if(std::abs(a) < 1e-12){

        varianceAdjustment =
            0.5
            *
            sigma
            *
            sigma
            *
            t
            *
            B
            *
            B;

    } else {

        varianceAdjustment =
            sigma
            *
            sigma
            /
            (4.0 * a)
            *
            (
                1.0
                -
                std::exp(
                    -2.0 * a * t
                )
            )
            *
            B
            *
            B;
    }

    return
        P0T
        /
        P0t
        *
        std::exp(
            B * f0t
            -
            varianceAdjustment
        );
}

/*
    Zero-coupon bond price:

        P(t,T) = A(t,T) exp(-B(t,T) r_t)
*/

double zeroCouponBondPrice(
    const HullWhiteModel& model,
    double t,
    double T,
    double r
){

    double A =
        AFunction(
            model,
            t,
            T
        );

    double B =
        model.B(
            t,
            T
        );

    return
        A
        *
        std::exp(
            -B * r
        );
}
