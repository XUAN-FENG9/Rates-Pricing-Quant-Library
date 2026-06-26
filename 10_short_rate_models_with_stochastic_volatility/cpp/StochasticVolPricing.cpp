#include "StochasticVolPricing.hpp"
#include <stdexcept>
#include <cmath>
#include <algorithm>

/*
    Find nearest time-grid index.
*/

int nearestTimeIndex(
    const std::vector<double>& times,
    double targetTime
){

    int bestIndex =
        0;

    double bestDiff =
        std::abs(
            times[0]
            -
            targetTime
        );

    for(size_t i = 1; i < times.size(); ++i){

        double diff =
            std::abs(
                times[i]
                -
                targetTime
            );

        if(diff < bestDiff){

            bestDiff = diff;

            bestIndex =
                static_cast<int>(i);
        }
    }

    return bestIndex;
}

/*
    Monte Carlo zero-coupon bond price:

        P(0,T) = E[ exp(- integral_0^T r_t dt) ]
*/

double monteCarloZeroCouponBondPrice(
    const StochasticVolSimulationResult& result,
    double maturity
){

    int idx =
        nearestTimeIndex(
            result.times,
            maturity
        );

    double sum =
        0.0;

    for(const auto& path : result.ratePaths){

        sum +=
            pathDiscountFactorFromZero(
                result.times,
                path,
                idx
            );
    }

    return
        sum
        /
        static_cast<double>(
            result.ratePaths.size()
        );
}

/*
    Monte Carlo option on a zero-coupon bond.

    Payoff at option expiry tau:

        max(P(tau,T) - K, 0)

    Here P(tau,T) is estimated pathwise using the simulated
    short-rate path between tau and T.
*/

double monteCarloBondOptionPrice(
    const StochasticVolSimulationResult& result,
    double optionExpiry,
    double bondMaturity,
    double strike,
    bool isCall
){

    int expiryIndex =
        nearestTimeIndex(
            result.times,
            optionExpiry
        );

    int maturityIndex =
        nearestTimeIndex(
            result.times,
            bondMaturity
        );

    if(maturityIndex <= expiryIndex){

        throw std::runtime_error(
            "bondMaturity must be greater than optionExpiry."
        );
    }

    double sum =
        0.0;

    for(const auto& path : result.ratePaths){

        double discount0Tau =
            pathDiscountFactorFromZero(
                result.times,
                path,
                expiryIndex
            );

        double bondTauT =
            pathDiscountFactor(
                result.times,
                path,
                expiryIndex,
                maturityIndex
            );

        double payoff;

        if(isCall){

            payoff =
                std::max(
                    bondTauT - strike,
                    0.0
                );

        } else {

            payoff =
                std::max(
                    strike - bondTauT,
                    0.0
                );
        }

        sum +=
            discount0Tau
            *
            payoff;
    }

    return
        sum
        /
        static_cast<double>(
            result.ratePaths.size()
        );
}
