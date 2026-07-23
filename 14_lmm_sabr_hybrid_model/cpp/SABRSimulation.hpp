#ifndef SABRSIMULATION_HPP_INCLUDED
#define SABRSIMULATION_HPP_INCLUDED

#include <cstddef>

#include "LMMSABRHybrid.hpp"
#include "Matrix.hpp"


struct SABRSimulationResult
{
    Vector times;

    Tensor3D forwardPaths;
    Tensor3D alphaPaths;

    std::size_t numberOfPaths() const;
    std::size_t numberOfTimes() const;
    std::size_t numberOfForwards() const;
};


Vector buildTimeGrid(
    double simulationEnd,
    std::size_t numberOfSteps,
    const Vector& mandatoryTimes = Vector()
);


std::size_t exactTimeIndex(
    const Vector& times,
    double targetTime,
    double tolerance = 1.0e-10
);


SABRSimulationResult simulateLMMSABR(
    const LMMSABRHybrid& model,
    double simulationEnd,
    std::size_t numberOfSteps,
    std::size_t numberOfPaths,
    unsigned int seed,
    bool antithetic,
    const Vector& mandatoryTimes = Vector()
);

#endif // SABRSIMULATION_HPP_INCLUDED
