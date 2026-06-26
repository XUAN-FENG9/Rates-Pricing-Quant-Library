#include "HullWhiteSimulation.hpp"

#include <random>
#include <cmath>

/*
    Simulate Hull-White short-rate paths using Euler discretisation.
*/

SimulationResult simulateShortRatePaths(
    const HullWhiteModel& model,
    double r0,
    double maturity,
    int nSteps,
    int nPaths,
    unsigned int seed
){

    double dt =
        maturity
        /
        static_cast<double>(nSteps);

    SimulationResult result;

    result.times.resize(
        nSteps + 1
    );

    for(int i = 0; i <= nSteps; ++i){

        result.times[i] =
            i * dt;
    }

    result.paths =
        std::vector<std::vector<double>>(
            nPaths,
            std::vector<double>(
                nSteps + 1,
                0.0
            )
        );

    for(int p = 0; p < nPaths; ++p){

        result.paths[p][0] =
            r0;
    }

    std::mt19937 generator(seed);

    std::normal_distribution<double> normal(
        0.0,
        1.0
    );

    for(int step = 0; step < nSteps; ++step){

        double t =
            result.times[step];

        for(int p = 0; p < nPaths; ++p){

            double z =
                normal(generator);

            result.paths[p][step + 1] =
                model.evolveShortRate(
                    t,
                    result.paths[p][step],
                    dt,
                    z
                );
        }
    }

    return result;
}

/*
    Pathwise discount factor:

        D(0,T) = exp(- integral r_t dt)
*/

double pathDiscountFactor(
    const std::vector<double>& times,
    const std::vector<double>& path
){

    double dt =
        times[1]
        -
        times[0];

    double integral =
        0.0;

    for(size_t i = 0; i < path.size() - 1; ++i){

        integral +=
            path[i]
            *
            dt;
    }

    return
        std::exp(
            -integral
        );
}

/*
    Monte Carlo zero-coupon bond price.
*/

double monteCarloZeroCouponBondPrice(
    const SimulationResult& result
){

    double sum =
        0.0;

    for(const auto& path : result.paths){

        sum +=
            pathDiscountFactor(
                result.times,
                path
            );
    }

    return
        sum
        /
        static_cast<double>(
            result.paths.size()
        );
}
