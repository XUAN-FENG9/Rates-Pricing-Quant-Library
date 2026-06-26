#include "StochasticVolSimulation.hpp"

#include <random>
#include <cmath>

/*
    Simulate correlated short-rate and variance paths.

    Correlated shocks:

        Z_vol = rho Z_rate + sqrt(1-rho^2) Z_independent
*/

StochasticVolSimulationResult simulateStochasticVolPaths(
    const StochasticVolModel& model,
    double r0,
    double v0,
    double maturity,
    int nSteps,
    int nPaths,
    unsigned int seed
){

    double dt =
        maturity
        /
        static_cast<double>(nSteps);

    StochasticVolSimulationResult result;

    result.times.resize(
        nSteps + 1
    );

    for(int i = 0; i <= nSteps; ++i){

        result.times[i] =
            i * dt;
    }

    result.ratePaths =
        std::vector<std::vector<double>>(
            nPaths,
            std::vector<double>(
                nSteps + 1,
                0.0
            )
        );

    result.variancePaths =
        std::vector<std::vector<double>>(
            nPaths,
            std::vector<double>(
                nSteps + 1,
                0.0
            )
        );

    for(int p = 0; p < nPaths; ++p){

        result.ratePaths[p][0] = r0;

        result.variancePaths[p][0] = v0;
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

            double zRate =
                normal(generator);

            double zIndependent =
                normal(generator);

            double zVol =
                model.rho * zRate
                +
                std::sqrt(
                    1.0
                    -
                    model.rho
                    *
                    model.rho
                )
                *
                zIndependent;

            double rNext;
            double vNext;

            model.evolve(
                t,
                result.ratePaths[p][step],
                result.variancePaths[p][step],
                dt,
                zRate,
                zVol,
                rNext,
                vNext
            );

            result.ratePaths[p][step + 1] =
                rNext;

            result.variancePaths[p][step + 1] =
                vNext;
        }
    }

    return result;
}

/*
    Discount factor from startIndex to endIndex:

        exp(- integral r_t dt)
*/

double pathDiscountFactor(
    const std::vector<double>& times,
    const std::vector<double>& ratePath,
    int startIndex,
    int endIndex
){

    double dt =
        times[1]
        -
        times[0];

    double integral =
        0.0;

    for(int i = startIndex; i < endIndex; ++i){

        integral +=
            ratePath[i]
            *
            dt;
    }

    return
        std::exp(
            -integral
        );
}

/*
    Discount factor from 0 to endIndex.
*/

double pathDiscountFactorFromZero(
    const std::vector<double>& times,
    const std::vector<double>& ratePath,
    int endIndex
){

    return
        pathDiscountFactor(
            times,
            ratePath,
            0,
            endIndex
        );
}
