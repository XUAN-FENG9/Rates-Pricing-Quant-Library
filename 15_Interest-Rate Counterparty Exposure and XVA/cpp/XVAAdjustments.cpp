#include "XVAAdjustments.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>


CreditCurve::CreditCurve(
    double hazardRate,
    double recoveryRate
)
    :
    hazardRate_(hazardRate),
    recoveryRate_(recoveryRate)
{
    validate();
}


double CreditCurve::hazardRate() const
{
    return hazardRate_;
}


double CreditCurve::recoveryRate() const
{
    return recoveryRate_;
}


double CreditCurve::lossGivenDefault() const
{
    return
        1.0
        -
        recoveryRate_;
}


double CreditCurve::survivalProbability(
    double time
) const
{
    return std::exp(
        -hazardRate_
        *
        time
    );
}


Vector CreditCurve::survivalProbabilities(
    const Vector& times
) const
{
    Vector result(
        times.size(),
        0.0
    );

    for (std::size_t index = 0;
         index < times.size();
         ++index)
    {
        result[index] =
            survivalProbability(
                times[index]
            );
    }

    return result;
}


Vector CreditCurve::defaultProbabilityIncrements(
    const Vector& times
) const
{
    Vector survival =
        survivalProbabilities(
            times
        );

    Vector increments(
        times.size(),
        0.0
    );

    double previousSurvival =
        1.0;

    for (std::size_t index = 0;
         index < times.size();
         ++index)
    {
        increments[index] =
            std::max(
                previousSurvival
                -
                survival[index],
                0.0
            );

        previousSurvival =
            survival[index];
    }

    return increments;
}


void CreditCurve::validate() const
{
    if (hazardRate_ < 0.0)
    {
        throw std::invalid_argument(
            "hazardRate must be non-negative."
        );
    }

    if (recoveryRate_ < 0.0 ||
        recoveryRate_ > 1.0)
    {
        throw std::invalid_argument(
            "recoveryRate must lie between zero and one."
        );
    }
}


void XVAResult::printSummary() const
{
    std::cout
        << "\n"
        << "XVA Summary\n"
        << "------------------------------\n"
        << "CVA: "
        << cva
        << "\n"
        << "DVA: "
        << dva
        << "\n"
        << "FCA: "
        << fca
        << "\n"
        << "FBA: "
        << fba
        << "\n"
        << "FVA: "
        << fva
        << "\n"
        << "Net valuation adjustment: "
        << netValuationAdjustment
        << "\n";
}


double calculateCVA(
    const Vector& times,
    const Vector& expectedExposure,
    const Vector& discountFactors,
    const CreditCurve& counterpartyCreditCurve
)
{
    if (times.size() !=
            expectedExposure.size()
        ||
        times.size() !=
            discountFactors.size())
    {
        throw std::invalid_argument(
            "CVA input dimensions are inconsistent."
        );
    }

    Vector defaultIncrements =
        counterpartyCreditCurve
        .defaultProbabilityIncrements(
            times
        );

    double cva =
        0.0;

    for (std::size_t index = 0;
         index < times.size();
         ++index)
    {
        cva +=
            discountFactors[index]
            *
            expectedExposure[index]
            *
            defaultIncrements[index];
    }

    return
        counterpartyCreditCurve
        .lossGivenDefault()
        *
        cva;
}


double calculateDVA(
    const Vector& times,
    const Vector& expectedNegativeExposure,
    const Vector& discountFactors,
    const CreditCurve& bankCreditCurve
)
{
    if (times.size() !=
            expectedNegativeExposure.size()
        ||
        times.size() !=
            discountFactors.size())
    {
        throw std::invalid_argument(
            "DVA input dimensions are inconsistent."
        );
    }

    Vector defaultIncrements =
        bankCreditCurve
        .defaultProbabilityIncrements(
            times
        );

    double dva =
        0.0;

    for (std::size_t index = 0;
         index < times.size();
         ++index)
    {
        dva +=
            discountFactors[index]
            *
            expectedNegativeExposure[index]
            *
            defaultIncrements[index];
    }

    return
        bankCreditCurve
        .lossGivenDefault()
        *
        dva;
}


void calculateFundingAdjustments(
    const Vector& times,
    const Vector& expectedExposure,
    const Vector& expectedNegativeExposure,
    const Vector& discountFactors,
    double borrowingSpread,
    double lendingSpread,
    double& fca,
    double& fba,
    double& fva
)
{
    if (borrowingSpread < 0.0 ||
        lendingSpread < 0.0)
    {
        throw std::invalid_argument(
            "Funding spreads must be non-negative."
        );
    }

    if (times.size() !=
            expectedExposure.size()
        ||
        times.size() !=
            expectedNegativeExposure.size()
        ||
        times.size() !=
            discountFactors.size())
    {
        throw std::invalid_argument(
            "Funding input dimensions are inconsistent."
        );
    }

    fca = 0.0;
    fba = 0.0;

    for (std::size_t index = 1;
         index < times.size();
         ++index)
    {
        double dt =
            times[index]
            -
            times[index - 1];

        fca +=
            discountFactors[index]
            *
            expectedExposure[index]
            *
            borrowingSpread
            *
            dt;

        fba +=
            discountFactors[index]
            *
            expectedNegativeExposure[index]
            *
            lendingSpread
            *
            dt;
    }

    fva =
        fca
        -
        fba;
}


Vector interpolateDiscountFactors(
    const Vector& tenorTimes,
    const Vector& initialDiscountFactors,
    const Vector& exposureTimes
)
{
    if (tenorTimes.size() !=
        initialDiscountFactors.size())
    {
        throw std::invalid_argument(
            "tenorTimes and discount factors "
            "must have equal size."
        );
    }

    if (tenorTimes.empty())
    {
        throw std::invalid_argument(
            "tenorTimes cannot be empty."
        );
    }

    Vector result(
        exposureTimes.size(),
        0.0
    );

    for (std::size_t exposureIndex = 0;
         exposureIndex <
             exposureTimes.size();
         ++exposureIndex)
    {
        double target =
            exposureTimes[exposureIndex];

        if (target <=
            tenorTimes.front())
        {
            result[exposureIndex] =
                initialDiscountFactors.front();

            continue;
        }

        if (target >=
            tenorTimes.back())
        {
            result[exposureIndex] =
                initialDiscountFactors.back();

            continue;
        }

        for (std::size_t tenorIndex = 0;
             tenorIndex + 1 <
                 tenorTimes.size();
             ++tenorIndex)
        {
            double leftTime =
                tenorTimes[tenorIndex];

            double rightTime =
                tenorTimes[tenorIndex + 1];

            if (target >= leftTime &&
                target <= rightTime)
            {
                double weight =
                    (
                        target
                        -
                        leftTime
                    )
                    /
                    (
                        rightTime
                        -
                        leftTime
                    );

                result[exposureIndex] =
                    initialDiscountFactors[tenorIndex]
                    *
                    (1.0 - weight)
                    +
                    initialDiscountFactors[tenorIndex + 1]
                    *
                    weight;

                break;
            }
        }
    }

    return result;
}


XVAResult calculateXVA(
    const Vector& tenorTimes,
    const Vector& initialDiscountFactors,
    const ExposureMetricsResult& exposureMetrics,
    const CreditCurve& counterpartyCreditCurve,
    const CreditCurve& bankCreditCurve,
    double borrowingSpread,
    double lendingSpread
)
{
    Vector discountFactors =
        interpolateDiscountFactors(
            tenorTimes,
            initialDiscountFactors,
            exposureMetrics.times
        );

    XVAResult result;

    result.cva =
        calculateCVA(
            exposureMetrics.times,
            exposureMetrics.expectedExposure,
            discountFactors,
            counterpartyCreditCurve
        );

    result.dva =
        calculateDVA(
            exposureMetrics.times,
            exposureMetrics.expectedNegativeExposure,
            discountFactors,
            bankCreditCurve
        );

    calculateFundingAdjustments(
        exposureMetrics.times,
        exposureMetrics.expectedExposure,
        exposureMetrics.expectedNegativeExposure,
        discountFactors,
        borrowingSpread,
        lendingSpread,
        result.fca,
        result.fba,
        result.fva
    );

    result.netValuationAdjustment =
        -result.cva
        +
        result.dva
        -
        result.fva;

    return result;
}
