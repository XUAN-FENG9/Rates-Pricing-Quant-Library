#include "BondOptionPricing.hpp"
#include "BondPricing.hpp"

#include <cmath>
#include <algorithm>

/*
    Standard normal CDF using erf.
*/

double normalCDF(
    double x
){

    return
        0.5
        *
        (
            1.0
            +
            std::erf(
                x
                /
                std::sqrt(2.0)
            )
        );
}

/*
    Effective zero-coupon bond option volatility.
*/

double bondOptionVolatility(
    const HullWhiteModel& model,
    double optionExpiry,
    double bondMaturity
){

    double a =
        model.a;

    double sigma =
        model.sigma;

    double tau =
        optionExpiry;

    double B =
        model.B(
            optionExpiry,
            bondMaturity
        );

    double variance;

    if(std::abs(a) < 1e-12){

        variance =
            sigma
            *
            sigma
            *
            tau
            *
            B
            *
            B;

    } else {

        variance =
            sigma
            *
            sigma
            *
            (
                1.0
                -
                std::exp(
                    -2.0 * a * tau
                )
            )
            /
            (2.0 * a)
            *
            B
            *
            B;
    }

    return
        std::sqrt(
            variance
        );
}

/*
    Analytic European option on a zero-coupon bond.

    Payoff:
        max(P(tau,T) - K, 0)
*/

double priceZeroCouponBondOption(
    const HullWhiteModel& model,
    double optionExpiry,
    double bondMaturity,
    double strike,
    bool isCall
){

    double P0Tau =
        model.curve->discount_factor(
            optionExpiry
        );

    double P0T =
        model.curve->discount_factor(
            bondMaturity
        );

    double sigmaP =
        bondOptionVolatility(
            model,
            optionExpiry,
            bondMaturity
        );

    if(sigmaP < 1e-12){

        double callPayoff =
            std::max(
                P0T
                -
                strike * P0Tau,
                0.0
            );

        double putPayoff =
            std::max(
                strike * P0Tau
                -
                P0T,
                0.0
            );

        return
            isCall
            ? callPayoff
            : putPayoff;
    }

    double h =
        std::log(
            P0T
            /
            (
                strike
                *
                P0Tau
            )
        )
        /
        sigmaP
        +
        0.5
        *
        sigmaP;

    if(isCall){

        return
            P0T
            *
            normalCDF(h)
            -
            strike
            *
            P0Tau
            *
            normalCDF(
                h - sigmaP
            );

    } else {

        return
            strike
            *
            P0Tau
            *
            normalCDF(
                -h + sigmaP
            )
            -
            P0T
            *
            normalCDF(-h);
    }
}

/*
    Monte Carlo zero-coupon bond option price.
*/

double monteCarloBondOptionPrice(
    const HullWhiteModel& model,
    const SimulationResult& result,
    double optionExpiry,
    double bondMaturity,
    double strike,
    bool isCall
){

    int idx =
        0;

    double minDiff =
        std::abs(
            result.times[0]
            -
            optionExpiry
        );

    for(size_t i = 1; i < result.times.size(); ++i){

        double diff =
            std::abs(
                result.times[i]
                -
                optionExpiry
            );

        if(diff < minDiff){

            minDiff = diff;
            idx = static_cast<int>(i);
        }
    }

    double dt =
        result.times[1]
        -
        result.times[0];

    double sum =
        0.0;

    for(const auto& path : result.paths){

        double rTau =
            path[idx];

        double PtauT =
            zeroCouponBondPrice(
                model,
                optionExpiry,
                bondMaturity,
                rTau
            );

        double payoff;

        if(isCall){

            payoff =
                std::max(
                    PtauT - strike,
                    0.0
                );

        } else {

            payoff =
                std::max(
                    strike - PtauT,
                    0.0
                );
        }

        double integral =
            0.0;

        for(int j = 0; j < idx; ++j){

            integral +=
                path[j]
                *
                dt;
        }

        double discount =
            std::exp(
                -integral
            );

        sum +=
            discount
            *
            payoff;
    }

    return
        sum
        /
        static_cast<double>(
            result.paths.size()
        );
}
