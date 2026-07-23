#include "LMMSABRPricing.hpp"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <stdexcept>


namespace
{
    std::size_t findResetIndex(
        const Vector& resetTimes,
        double targetTime,
        double tolerance = 1.0e-10
    )
    {
        for (std::size_t i = 0;
             i < resetTimes.size();
             ++i)
        {
            if (std::fabs(
                    resetTimes[i]
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
            "Requested reset time is not "
            "present in the tenor structure."
        );
    }


    double sampleStandardError(
        const Vector& values
    )
    {
        if (values.size() < 2)
        {
            return 0.0;
        }

        double mean =
            std::accumulate(
                values.begin(),
                values.end(),
                0.0
            )
            /
            static_cast<double>(
                values.size()
            );

        double squaredDeviationSum =
            0.0;

        for (double value :
             values)
        {
            double deviation =
                value - mean;

            squaredDeviationSum +=
                deviation
                *
                deviation;
        }

        double sampleVariance =
            squaredDeviationSum
            /
            static_cast<double>(
                values.size() - 1
            );

        return std::sqrt(
            sampleVariance
            /
            static_cast<double>(
                values.size()
            )
        );
    }
}


Vector bondPricesFromForwards(
    const Vector& forwards,
    const Vector& accruals,
    std::size_t startForwardIndex
)
{
    if (forwards.size() !=
        accruals.size())
    {
        throw std::invalid_argument(
            "forwards and accruals must "
            "have the same size."
        );
    }

    if (startForwardIndex >
        forwards.size())
    {
        throw std::out_of_range(
            "Invalid startForwardIndex."
        );
    }

    Vector bonds(
        forwards.size() + 1,
        0.0
    );

    bonds[startForwardIndex] = 1.0;

    for (std::size_t i = startForwardIndex;
         i < forwards.size();
         ++i)
    {
        double denominator =
            1.0
            +
            accruals[i]
            *
            forwards[i];

        if (denominator <= 0.0)
        {
            throw std::runtime_error(
                "Invalid forward-to-bond denominator."
            );
        }

        bonds[i + 1] =
            bonds[i]
            /
            denominator;
    }

    return bonds;
}


void swapAnnuityAndRate(
    const Vector& forwards,
    const Vector& accruals,
    std::size_t swapStartIndex,
    std::size_t swapEndIndex,
    double& annuity,
    double& swapRate
)
{
    if (swapStartIndex >=
        swapEndIndex)
    {
        throw std::invalid_argument(
            "swapStartIndex must be smaller "
            "than swapEndIndex."
        );
    }

    if (swapEndIndex >
        forwards.size())
    {
        throw std::out_of_range(
            "swapEndIndex exceeds "
            "the forward dimension."
        );
    }

    Vector bonds =
        bondPricesFromForwards(
            forwards,
            accruals,
            swapStartIndex
        );

    annuity = 0.0;

    for (std::size_t i = swapStartIndex;
         i < swapEndIndex;
         ++i)
    {
        annuity +=
            accruals[i]
            *
            bonds[i + 1];
    }

    if (annuity <= 0.0)
    {
        throw std::runtime_error(
            "Swap annuity must be positive."
        );
    }

    swapRate =
        (
            1.0
            -
            bonds[swapEndIndex]
        )
        /
        annuity;
}


MonteCarloPriceResult priceCapletMC(
    const LMMSABRHybrid& model,
    const SABRSimulationResult& simulation,
    double resetTime,
    double strike,
    double notional
)
{
    if (notional <= 0.0)
    {
        throw std::invalid_argument(
            "notional must be positive."
        );
    }

    std::size_t forwardIndex =
        findResetIndex(
            model.resetTimes(),
            resetTime
        );

    std::size_t simulationIndex =
        exactTimeIndex(
            simulation.times,
            resetTime
        );

    std::size_t numberOfPaths =
        simulation.numberOfPaths();

    double accrual =
        model.accruals()[forwardIndex];

    Vector discountedValues(
        numberOfPaths,
        0.0
    );

    for (std::size_t path = 0;
         path < numberOfPaths;
         ++path)
    {
        const Vector& forwardsAtReset =
            simulation
                .forwardPaths
                [path]
                [simulationIndex];

        double fixingForward =
            forwardsAtReset[
                forwardIndex
            ];

        double paymentPayoff =
            notional
            *
            accrual
            *
            std::max(
                fixingForward
                -
                strike,
                0.0
            );

        double resetDateValue =
            paymentPayoff
            /
            (
                1.0
                +
                accrual
                *
                fixingForward
            );

        double terminalBond =
            model.terminalBondFromForwards(
                forwardsAtReset,
                forwardIndex
            );

        discountedValues[path] =
            resetDateValue
            /
            terminalBond;
    }

    double meanNumeraireValue =
        std::accumulate(
            discountedValues.begin(),
            discountedValues.end(),
            0.0
        )
        /
        static_cast<double>(
            numberOfPaths
        );

    double initialTerminalBond =
        model.initialTerminalBond();

    MonteCarloPriceResult result;

    result.price =
        initialTerminalBond
        *
        meanNumeraireValue;

    result.standardError =
        initialTerminalBond
        *
        sampleStandardError(
            discountedValues
        );

    result.meanPayoff =
        meanNumeraireValue;

    result.numberOfPaths =
        numberOfPaths;

    return result;
}


MonteCarloPriceResult pricePayerSwaptionMC(
    const LMMSABRHybrid& model,
    const SABRSimulationResult& simulation,
    double expiry,
    double swapEnd,
    double strike,
    double notional
)
{
    if (notional <= 0.0)
    {
        throw std::invalid_argument(
            "notional must be positive."
        );
    }

    std::size_t swapStartIndex =
        findResetIndex(
            model.resetTimes(),
            expiry
        );

    std::size_t swapEndIndex =
        findResetIndex(
            model.resetTimes(),
            swapEnd
        );

    if (swapEndIndex <=
        swapStartIndex)
    {
        throw std::invalid_argument(
            "swapEnd must be after expiry."
        );
    }

    std::size_t simulationIndex =
        exactTimeIndex(
            simulation.times,
            expiry
        );

    std::size_t numberOfPaths =
        simulation.numberOfPaths();

    Vector numeraireValues(
        numberOfPaths,
        0.0
    );

    for (std::size_t path = 0;
         path < numberOfPaths;
         ++path)
    {
        const Vector& forwardsAtExpiry =
            simulation
                .forwardPaths
                [path]
                [simulationIndex];

        double annuity = 0.0;
        double swapRate = 0.0;

        swapAnnuityAndRate(
            forwardsAtExpiry,
            model.accruals(),
            swapStartIndex,
            swapEndIndex,
            annuity,
            swapRate
        );

        double payoff =
            notional
            *
            annuity
            *
            std::max(
                swapRate
                -
                strike,
                0.0
            );

        double terminalBond =
            model.terminalBondFromForwards(
                forwardsAtExpiry,
                swapStartIndex
            );

        numeraireValues[path] =
            payoff
            /
            terminalBond;
    }

    double meanNumeraireValue =
        std::accumulate(
            numeraireValues.begin(),
            numeraireValues.end(),
            0.0
        )
        /
        static_cast<double>(
            numberOfPaths
        );

    double initialTerminalBond =
        model.initialTerminalBond();

    MonteCarloPriceResult result;

    result.price =
        initialTerminalBond
        *
        meanNumeraireValue;

    result.standardError =
        initialTerminalBond
        *
        sampleStandardError(
            numeraireValues
        );

    result.meanPayoff =
        meanNumeraireValue;

    result.numberOfPaths =
        numberOfPaths;

    return result;
}
