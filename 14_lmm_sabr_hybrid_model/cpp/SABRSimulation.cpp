#include "SABRSimulation.hpp"

#include <algorithm>
#include <cmath>
#include <random>
#include <stdexcept>


std::size_t SABRSimulationResult::numberOfPaths() const
{
    return forwardPaths.size();
}


std::size_t SABRSimulationResult::numberOfTimes() const
{
    if (forwardPaths.empty())
    {
        return 0;
    }

    return forwardPaths.front().size();
}


std::size_t SABRSimulationResult::numberOfForwards() const
{
    if (forwardPaths.empty() ||
        forwardPaths.front().empty())
    {
        return 0;
    }

    return forwardPaths
        .front()
        .front()
        .size();
}


Vector buildTimeGrid(
    double simulationEnd,
    std::size_t numberOfSteps,
    const Vector& mandatoryTimes
)
{
    if (simulationEnd <= 0.0)
    {
        throw std::invalid_argument(
            "simulationEnd must be positive."
        );
    }

    if (numberOfSteps == 0)
    {
        throw std::invalid_argument(
            "numberOfSteps must be positive."
        );
    }

    Vector times;

    times.reserve(
        numberOfSteps
        +
        mandatoryTimes.size()
        +
        1
    );

    double dt =
        simulationEnd
        /
        static_cast<double>(
            numberOfSteps
        );

    for (std::size_t i = 0;
         i <= numberOfSteps;
         ++i)
    {
        times.push_back(
            static_cast<double>(i)
            *
            dt
        );
    }

    for (double mandatoryTime :
         mandatoryTimes)
    {
        if (mandatoryTime >= 0.0 &&
            mandatoryTime <= simulationEnd)
        {
            times.push_back(
                mandatoryTime
            );
        }
    }

    std::sort(
        times.begin(),
        times.end()
    );

    Vector uniqueTimes;

    for (double time :
         times)
    {
        if (uniqueTimes.empty() ||
            std::fabs(
                time
                -
                uniqueTimes.back()
            )
            >
            1.0e-12)
        {
            uniqueTimes.push_back(
                time
            );
        }
    }

    return uniqueTimes;
}


std::size_t exactTimeIndex(
    const Vector& times,
    double targetTime,
    double tolerance
)
{
    for (std::size_t i = 0;
         i < times.size();
         ++i)
    {
        if (std::fabs(
                times[i]
                -
                targetTime
            )
            <=
            tolerance)
        {
            return i;
        }
    }

    throw std::runtime_error(
        "The requested time is not "
        "present on the simulation grid."
    );
}


SABRSimulationResult simulateLMMSABR(
    const LMMSABRHybrid& model,
    double simulationEnd,
    std::size_t numberOfSteps,
    std::size_t numberOfPaths,
    unsigned int seed,
    bool antithetic,
    const Vector& mandatoryTimes
)
{
    if (numberOfPaths == 0)
    {
        throw std::invalid_argument(
            "numberOfPaths must be positive."
        );
    }

    Vector times =
        buildTimeGrid(
            simulationEnd,
            numberOfSteps,
            mandatoryTimes
        );

    std::size_t numberOfTimes =
        times.size();

    std::size_t numberOfForwards =
        model.numberOfForwards();

    std::size_t numberOfFactors =
        model.numberOfFactors();

    SABRSimulationResult result;

    result.times = times;

    result.forwardPaths =
        Tensor3D(
            numberOfPaths,
            std::vector<Vector>(
                numberOfTimes,
                Vector(
                    numberOfForwards,
                    0.0
                )
            )
        );

    result.alphaPaths =
        Tensor3D(
            numberOfPaths,
            std::vector<Vector>(
                numberOfTimes,
                Vector(
                    numberOfForwards,
                    0.0
                )
            )
        );

    for (std::size_t path = 0;
         path < numberOfPaths;
         ++path)
    {
        result.forwardPaths[path][0] =
            model.initialForwards();

        result.alphaPaths[path][0] =
            model.sabrParameters().alpha0();
    }

    std::mt19937 generator(
        seed
    );

    std::normal_distribution<double>
        standardNormal(
            0.0,
            1.0
        );

    for (std::size_t timeIndex = 0;
         timeIndex + 1 < numberOfTimes;
         ++timeIndex)
    {
        double currentTime =
            times[timeIndex];

        double dt =
            times[timeIndex + 1]
            -
            times[timeIndex];

        Vector storedRateShocks;
        Vector storedVolatilityShocks;

        for (std::size_t path = 0;
             path < numberOfPaths;
             ++path)
        {
            Vector rateFactorShocks(
                numberOfFactors,
                0.0
            );

            Vector independentVolatilityShocks(
                numberOfForwards,
                0.0
            );

            bool useAntitheticPath =
                antithetic
                &&
                path % 2 == 1;

            if (!useAntitheticPath)
            {
                for (std::size_t factor = 0;
                     factor < numberOfFactors;
                     ++factor)
                {
                    rateFactorShocks[factor] =
                        standardNormal(
                            generator
                        );
                }

                for (std::size_t i = 0;
                     i < numberOfForwards;
                     ++i)
                {
                    independentVolatilityShocks[i] =
                        standardNormal(
                            generator
                        );
                }

                storedRateShocks =
                    rateFactorShocks;

                storedVolatilityShocks =
                    independentVolatilityShocks;
            }
            else
            {
                for (std::size_t factor = 0;
                     factor < numberOfFactors;
                     ++factor)
                {
                    rateFactorShocks[factor] =
                        -storedRateShocks[factor];
                }

                for (std::size_t i = 0;
                     i < numberOfForwards;
                     ++i)
                {
                    independentVolatilityShocks[i] =
                        -storedVolatilityShocks[i];
                }
            }

            Vector nextForwards;
            Vector nextAlpha;

            model.evolve(
                currentTime,
                result.forwardPaths
                    [path]
                    [timeIndex],
                result.alphaPaths
                    [path]
                    [timeIndex],
                dt,
                rateFactorShocks,
                independentVolatilityShocks,
                nextForwards,
                nextAlpha
            );

            result.forwardPaths
                [path]
                [timeIndex + 1]
                =
                nextForwards;

            result.alphaPaths
                [path]
                [timeIndex + 1]
                =
                nextAlpha;
        }
    }

    return result;
}
