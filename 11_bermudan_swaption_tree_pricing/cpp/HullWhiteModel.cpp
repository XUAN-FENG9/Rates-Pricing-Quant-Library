#include "HullWhiteModel.hpp"

#include <cmath>
#include <stdexcept>

/*
    Constructor
*/

HullWhiteModel::HullWhiteModel(
    double meanReversion,
    double volatility,
    YieldCurve* curve_
){
    a = meanReversion;
    sigma = volatility;
    curve = curve_;
}

/*
    Hull-White B(t,T):

        B(t,T) = (1 - exp(-a(T-t))) / a

    This measures bond price sensitivity to the short rate.
*/

double HullWhiteModel::B(
    double t,
    double T
) const {

    if(T < t){
        throw std::runtime_error(
            "T must be greater than or equal to t."
        );
    }

    if(std::abs(a) < 1e-12){
        return T - t;
    }

    return
        (
            1.0
            -
            std::exp(
                -a * (T - t)
            )
        )
        /
        a;
}

/*
    Approximate instantaneous forward rate:

        f(0,t) = - d log P(0,t) / dt

    We use a practical bump because the curve is interpolated from
    discrete market pillars. Very small bumps may create numerical noise.
*/

double HullWhiteModel::instantaneousForwardRate(
    double t,
    double bump
) const {

    double t1 =
        std::max(
            t - bump,
            1e-6
        );

    double t2 =
        t + bump;

    double p1 =
        curve->discount_factor(t1);

    double p2 =
        curve->discount_factor(t2);

    return
        -(
            std::log(p2)
            -
            std::log(p1)
        )
        /
        (t2 - t1);
}

/*
    Numerical derivative of instantaneous forward rate.

        df(0,t) / dt
*/

double HullWhiteModel::instantaneousForwardDerivative(
    double t,
    double bump
) const {

    double t1 =
        std::max(
            t - bump,
            1e-6
        );

    double t2 =
        t + bump;

    double f1 =
        instantaneousForwardRate(t1);

    double f2 =
        instantaneousForwardRate(t2);

    return
        (f2 - f1)
        /
        (t2 - t1);
}

/*
    Hull-White theta(t):

        theta(t)
        =
        df(0,t)/dt
        + a f(0,t)
        + sigma^2/(2a) * (1 - exp(-2at))

    This drift term makes the model fit the initial yield curve.
*/

double HullWhiteModel::theta(
    double t
) const {

    double f =
        instantaneousForwardRate(t);

    double dfdt =
        instantaneousForwardDerivative(t);

    double convexity;

    if(std::abs(a) < 1e-12){

        convexity =
            sigma
            *
            sigma
            *
            t;

    } else {

        convexity =
            sigma
            *
            sigma
            /
            (2.0 * a)
            *
            (
                1.0
                -
                std::exp(
                    -2.0 * a * t
                )
            );
    }

    return
        dfdt
        +
        a * f
        +
        convexity;
}

/*
    Short-rate drift:

        theta(t) - a r(t)
*/

double HullWhiteModel::shortRateDrift(
    double t,
    double r
) const {

    return
        theta(t)
        -
        a * r;
}

/*
    Euler step:

        r_{t+dt}
        =
        r_t
        +
        [theta(t) - a r_t] dt
        +
        sigma sqrt(dt) Z
*/

double HullWhiteModel::evolveShortRate(
    double t,
    double r,
    double dt,
    double z
) const {

    return
        r
        +
        shortRateDrift(t, r) * dt
        +
        sigma
        *
        std::sqrt(dt)
        *
        z;
}
