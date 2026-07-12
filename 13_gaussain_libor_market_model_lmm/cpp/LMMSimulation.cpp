#include "LMMSimulation.hpp"

#include <cmath>
#include <limits>
#include <random>
#include <stdexcept>

LMMSimulationResult simulateGaussianLMM(
    const GaussianLMM& model,
    double simulationEnd,
    int numberOfSteps,
    int numberOfPaths,
    unsigned int seed,
    bool antithetic
){

    if(simulationEnd <= 0.0){

        throw std::invalid_argument(
            "Simulation end must be positive."
        );
    }

    if(numberOfSteps <= 0){

        throw std::invalid_argument(
            "Number of simulation steps must be positive."
        );
    }

    if(numberOfPaths <= 0){

        throw std::invalid_argument(
            "Number of simulation paths must be positive."
        );
    }

    double dt =
        simulationEnd
        /
        static_cast<double>(
            numberOfSteps
        );

    LMMSimulationResult result;

    result.times.resize(
        numberOfSteps + 1
    );

    for(int step = 0; step <= numberOfSteps; ++step){

        result.times[step] =
            step
            *
            dt;
    }

    result.forwardPaths =
        std::vector<
            std::vector<
                std::vector<double>
            >
        >(
            numberOfPaths,
            std::vector<
                std::vector<double>
            >(
                numberOfSteps + 1,
                std::vector<double>(
                    model.numberOfForwards(),
                    0.0
                )
            )
        );

    for(int path = 0; path < numberOfPaths; ++path){

        result.forwardPaths[path][0] =
            model.initialForwards();
    }

    std::mt19937 generator(
        seed
    );

    std::normal_distribution<double> normal(
        0.0,
        1.0
    );

    for(int step = 0; step < numberOfSteps; ++step){

        double time =
            result.times[step];

        int halfPaths =
            (numberOfPaths + 1)
            /
            2;

        std::vector<std::vector<double>> baseShocks(
            halfPaths,
            std::vector<double>(
                model.numberOfFactors(),
                0.0
            )
        );

        for(int path = 0; path < halfPaths; ++path){

            for(int factor = 0; factor < model.numberOfFactors(); ++factor){

                baseShocks[path][factor] =
                    normal(
                        generator
                    );
            }
        }

        for(int path = 0; path < numberOfPaths; ++path){

            std::vector<double> shocks(
                model.numberOfFactors(),
                0.0
            );

            if(antithetic){

                int basePath =
                    path % halfPaths;

                double sign =
                    path < halfPaths
                    ?
                    1.0
                    :
                    -1.0;

                for(int factor = 0; factor < model.numberOfFactors(); ++factor){

                    shocks[factor] =
                        sign
                        *
                        baseShocks[basePath][factor];
                }

            } else {

                for(int factor = 0; factor < model.numberOfFactors(); ++factor){

                    shocks[factor] =
                        normal(
                            generator
                        );
                }
            }

            result.forwardPaths[path][step + 1] =
                model.evolve(
                    time,
                    result.forwardPaths[path][step],
                    dt,
                    shocks
                );
        }
    }

    return result;
}

int nearestSimulationIndex(
    const std::vector<double>& times,
    double targetTime
){

    int bestIndex =
        0;

    double bestDifference =
        std::numeric_limits<double>::max();

    for(std::size_t i = 0; i < times.size(); ++i){

        double difference =
            std::abs(
                times[i]
                -
                targetTime
            );

        if(difference < bestDifference){

            bestDifference =
                difference;

            bestIndex =
                static_cast<int>(i);
        }
    }

    return bestIndex;
}
