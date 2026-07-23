#include <cmath>
#include <iomanip>
#include <iostream>

#include "LMMSABRHybrid.hpp"
#include "LMMSABRPricing.hpp"
#include "SABRParameters.hpp"
#include "SABRSimulation.hpp"


Matrix buildSimpleFactorLoadings(
    const Vector& resetTimes
)
{
    Matrix loadings(
        resetTimes.size(),
        Vector(
            3,
            0.0
        )
    );

    for (std::size_t i = 0;
         i < resetTimes.size();
         ++i)
    {
        double maturity =
            resetTimes[i];

        loadings[i][0] =
            0.90;

        loadings[i][1] =
            0.30
            *
            std::exp(
                -0.10
                *
                maturity
            );

        loadings[i][2] =
            0.15
            *
            (
                maturity
                -
                5.0
            )
            /
            5.0;
    }

    return loadings;
}


int main()
{
    try
    {
        std::cout
            << std::fixed
            << std::setprecision(8);

        double tenorStep =
            0.5;

        std::size_t numberOfForwards =
            20;

        Vector resetTimes(
            numberOfForwards,
            0.0
        );

        Vector accruals(
            numberOfForwards,
            tenorStep
        );

        Vector initialForwards(
            numberOfForwards,
            0.045
        );

        for (std::size_t i = 0;
             i < numberOfForwards;
             ++i)
        {
            resetTimes[i] =
                static_cast<double>(i)
                *
                tenorStep;

            initialForwards[i] =
                0.040
                +
                0.00030
                *
                static_cast<double>(i);
        }

        Vector initialDiscountFactors(
            numberOfForwards + 1,
            1.0
        );

        for (std::size_t i = 0;
             i < numberOfForwards;
             ++i)
        {
            initialDiscountFactors[i + 1] =
                initialDiscountFactors[i]
                /
                (
                    1.0
                    +
                    accruals[i]
                    *
                    initialForwards[i]
                );
        }

        Matrix correlationLoadings =
            buildSimpleFactorLoadings(
                resetTimes
            );

        SABRParameters sabrParameters(
            numberOfForwards,
            0.18,
            0.50,
            -0.25,
            0.40,
            0.03,
            1.0e-8,
            10.0
        );

        LMMSABRHybrid model(
            resetTimes,
            accruals,
            initialForwards,
            initialDiscountFactors,
            correlationLoadings,
            sabrParameters,
            0.25,
            0.05,
            0.05
        );

        model.printSummary();

        std::cout
            << "\n";

        sabrParameters.printSummary();

        Vector initialDrift =
            model.terminalMeasureDrift(
                0.0,
                model.initialForwards(),
                model.sabrParameters().alpha0()
            );

        std::cout
            << "\n"
            << "Initial final-forward drift: "
            << initialDrift.back()
            << "\n";

        Vector mandatoryTimes =
        {
            0.5,
            1.0,
            1.5,
            2.0,
            5.0
        };

        SABRSimulationResult simulation =
            simulateLMMSABR(
                model,
                5.0,
                100,
                2000,
                42,
                true,
                mandatoryTimes
            );

        std::cout
            << "\n"
            << "Simulation dimensions\n"
            << "Paths: "
            << simulation.numberOfPaths()
            << "\n"
            << "Times: "
            << simulation.numberOfTimes()
            << "\n"
            << "Forwards: "
            << simulation.numberOfForwards()
            << "\n";

        MonteCarloPriceResult caplet =
            priceCapletMC(
                model,
                simulation,
                2.0,
                0.045,
                1000000.0
            );

        std::cout
            << "\n"
            << "Caplet Price\n"
            << "Price: "
            << caplet.price
            << "\n"
            << "Standard error: "
            << caplet.standardError
            << "\n";

        MonteCarloPriceResult swaption =
            pricePayerSwaptionMC(
                model,
                simulation,
                2.0,
                5.0,
                0.045,
                1000000.0
            );

        std::cout
            << "\n"
            << "Payer Swaption Price\n"
            << "Price: "
            << swaption.price
            << "\n"
            << "Standard error: "
            << swaption.standardError
            << "\n";

        std::size_t timeIndex =
            exactTimeIndex(
                simulation.times,
                2.0
            );

        std::cout
            << "\n"
            << "Example state at t = 2.0\n"
            << "Forward L8: "
            << simulation
                .forwardPaths
                [0]
                [timeIndex]
                [8]
            << "\n"
            << "Alpha 8: "
            << simulation
                .alphaPaths
                [0]
                [timeIndex]
                [8]
            << "\n";

        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr
            << "Error: "
            << error.what()
            << "\n";

        return 1;
    }
}
