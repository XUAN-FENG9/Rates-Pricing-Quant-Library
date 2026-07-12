#include "Diagnostics.hpp"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>

void printForwardCurve(
    const GaussianLMM& model
){

    std::cout
        << "\nInitial Forward Curve"
        << std::endl;

    std::cout
        << "============================================================"
        << std::endl;

    std::cout
        << std::setw(8)
        << "Index"
        << std::setw(14)
        << "Reset"
        << std::setw(14)
        << "Payment"
        << std::setw(18)
        << "Forward"
        << std::endl;

    for(int i = 0; i < model.numberOfForwards(); ++i){

        std::cout
            << std::setw(8)
            << i
            << std::setw(14)
            << model.tenor().times()[i]
            << std::setw(14)
            << model.tenor().times()[i + 1]
            << std::setw(18)
            << model.initialForwards()[i]
            << std::endl;
    }
}

void printCorrelationSummary(
    const Matrix& correlationMatrix
){

    double minimum =
        std::numeric_limits<double>::max();

    double maximum =
        -std::numeric_limits<double>::max();

    for(const auto& row : correlationMatrix){

        for(double value : row){

            minimum =
                std::min(
                    minimum,
                    value
                );

            maximum =
                std::max(
                    maximum,
                    value
                );
        }
    }

    std::cout
        << "\nCorrelation Summary"
        << std::endl;

    std::cout
        << "============================================================"
        << std::endl;

    std::cout
        << "Matrix size : "
        << correlationMatrix.size()
        << " x "
        << correlationMatrix.size()
        << std::endl;

    std::cout
        << "Minimum     : "
        << minimum
        << std::endl;

    std::cout
        << "Maximum     : "
        << maximum
        << std::endl;
}

void printSimulationSummary(
    const GaussianLMM& model,
    const LMMSimulationResult& simulation
){

    std::cout
        << "\nSimulation Summary"
        << std::endl;

    std::cout
        << "============================================================"
        << std::endl;

    std::cout
        << "Paths       : "
        << simulation.forwardPaths.size()
        << std::endl;

    std::cout
        << "Time points : "
        << simulation.times.size()
        << std::endl;

    std::cout
        << "Forwards    : "
        << model.numberOfForwards()
        << std::endl;

    std::cout
        << "Factors     : "
        << model.numberOfFactors()
        << std::endl;

    std::cout
        << "Terminal DF : "
        << model.initialTerminalDiscountFactor()
        << std::endl;
}

void printPricingSummary(
    double capletPrice,
    double swaptionPrice
){

    std::cout
        << "\nGaussian LMM Pricing Summary"
        << std::endl;

    std::cout
        << "============================================================"
        << std::endl;

    std::cout
        << "Caplet price          : "
        << capletPrice
        << std::endl;

    std::cout
        << "Payer swaption price : "
        << swaptionPrice
        << std::endl;
}
