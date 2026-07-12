#include "LMMPricing.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

std::vector<double> bondPricesFromForwards(
    const std::vector<double>& forwards,
    const TenorStructure& tenor,
    int startForwardIndex
){

    int numberOfForwards =
        tenor.numberOfForwards();

    std::vector<double> bonds(
        numberOfForwards + 1,
        std::numeric_limits<double>::quiet_NaN()
    );

    bonds[startForwardIndex] =
        1.0;

    double runningBond =
        1.0;

    for(int j = startForwardIndex; j < numberOfForwards; ++j){

        double denominator =
            1.0
            +
            tenor.accruals()[j]
            *
            forwards[j];

        if(denominator <= 0.0){

            throw std::runtime_error(
                "Invalid forward state in bond reconstruction."
            );
        }

        runningBond /=
            denominator;

        bonds[j + 1] =
            runningBond;
    }

    return bonds;
}

SwapState swapAnnuityAndRate(
    const std::vector<double>& forwards,
    const TenorStructure& tenor,
    int swapStartIndex,
    int swapEndIndex
){

    if(swapEndIndex <= swapStartIndex){

        throw std::invalid_argument(
            "Swap end must be after swap start."
        );
    }

    std::vector<double> bonds =
        bondPricesFromForwards(
            forwards,
            tenor,
            swapStartIndex
        );

    double annuity =
        0.0;

    for(int j = swapStartIndex; j < swapEndIndex; ++j){

        annuity +=
            tenor.accruals()[j]
            *
            bonds[j + 1];
    }

    double swapRate =
        0.0;

    if(annuity > 0.0){

        swapRate =
            (
                1.0
                -
                bonds[swapEndIndex]
            )
            /
            annuity;
    }

    return {
        annuity,
        swapRate
    };
}

double priceCapletMonteCarlo(
    const GaussianLMM& model,
    const LMMSimulationResult& simulation,
    double resetTime,
    double strike,
    double notional
){

    int forwardIndex =
        model.tenor().forwardIndex(
            resetTime
        );

    int simulationIndex =
        nearestSimulationIndex(
            simulation.times,
            resetTime
        );

    double terminalDiscountFactor =
        model.initialTerminalDiscountFactor();

    double sum =
        0.0;

    int numberOfPaths =
        static_cast<int>(
            simulation.forwardPaths.size()
        );

    for(int path = 0; path < numberOfPaths; ++path){

        const std::vector<double>& forwards =
            simulation.forwardPaths[path][simulationIndex];

        double forward =
            forwards[forwardIndex];

        double accrual =
            model.tenor().accruals()[forwardIndex];

        double paymentTimePayoff =
            notional
            *
            accrual
            *
            std::max(
                forward
                -
                strike,
                0.0
            );

        /*
            Discount caplet payment from T_{i+1} to reset T_i.
        */

        double resetDateValue =
            paymentTimePayoff
            /
            (
                1.0
                +
                accrual
                *
                forward
            );

        double terminalBond =
            model.terminalBondFromForwards(
                forwards,
                forwardIndex
            );

        sum +=
            resetDateValue
            /
            terminalBond;
    }

    return
        terminalDiscountFactor
        *
        sum
        /
        static_cast<double>(
            numberOfPaths
        );
}

double pricePayerSwaptionMonteCarlo(
    const GaussianLMM& model,
    const LMMSimulationResult& simulation,
    double expiry,
    double swapEnd,
    double strike,
    double notional
){

    int expiryIndex =
        model.tenor().timeIndex(
            expiry
        );

    int swapEndIndex =
        model.tenor().timeIndex(
            swapEnd
        );

    int simulationIndex =
        nearestSimulationIndex(
            simulation.times,
            expiry
        );

    int numberOfPaths =
        static_cast<int>(
            simulation.forwardPaths.size()
        );

    double sum =
        0.0;

    for(int path = 0; path < numberOfPaths; ++path){

        const std::vector<double>& forwards =
            simulation.forwardPaths[path][simulationIndex];

        SwapState swapState =
            swapAnnuityAndRate(
                forwards,
                model.tenor(),
                expiryIndex,
                swapEndIndex
            );

        double payoff =
            notional
            *
            swapState.annuity
            *
            std::max(
                swapState.swapRate
                -
                strike,
                0.0
            );

        double terminalBond =
            model.terminalBondFromForwards(
                forwards,
                expiryIndex
            );

        sum +=
            payoff
            /
            terminalBond;
    }

    return
        model.initialTerminalDiscountFactor()
        *
        sum
        /
        static_cast<double>(
            numberOfPaths
        );
}
