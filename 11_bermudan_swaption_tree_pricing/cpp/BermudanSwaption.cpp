#include "BermudanSwaption.hpp"

#include "BondPricing.hpp"

#include <cmath>
#include <numeric>
#include <algorithm>

/*
    Constructor.

    We cache payment schedules for all standard exercise dates.
*/

BermudanSwaption::BermudanSwaption(
    double notional_,
    double fixedRate_,
    double optionStart_,
    double optionEnd_,
    double swapTenor_,
    int paymentFrequency_,
    int exerciseFrequency_,
    bool payer_
){

    notional = notional_;
    fixedRate = fixedRate_;

    optionStart = optionStart_;
    optionEnd = optionEnd_;
    swapTenor = swapTenor_;

    paymentFrequency = paymentFrequency_;
    exerciseFrequency = exerciseFrequency_;

    payer = payer_;

    exerciseDates =
        generateExerciseDates(
            optionStart,
            optionEnd,
            exerciseFrequency
        );

    for(double exerciseTime : exerciseDates){

        double key =
            std::round(
                exerciseTime
                *
                1e10
            )
            /
            1e10;

        paymentScheduleCache[key] =
            generatePaymentDates(
                exerciseTime,
                exerciseTime + swapTenor,
                paymentFrequency
            );
    }
}

/*
    Return payment dates for swap entered at exerciseTime.
*/

std::vector<double> BermudanSwaption::paymentDates(
    double exerciseTime
) const {

    double key =
        std::round(
            exerciseTime
            *
            1e10
        )
        /
        1e10;

    auto it =
        paymentScheduleCache.find(
            key
        );

    if(it != paymentScheduleCache.end()){

        return it->second;
    }

    return generatePaymentDates(
        exerciseTime,
        exerciseTime + swapTenor,
        paymentFrequency
    );
}

/*
    Fixed-leg annuity:

        A(t) = sum accrual * P(t,T_i)
*/

double BermudanSwaption::annuity(
    const HullWhiteModel& model,
    double exerciseTime,
    double shortRate
) const {

    std::vector<double> payDates =
        paymentDates(
            exerciseTime
        );

    double accrual =
        1.0
        /
        static_cast<double>(
            paymentFrequency
        );

    double sum =
        0.0;

    for(double T : payDates){

        double df =
            zeroCouponBondPrice(
                model,
                exerciseTime,
                T,
                shortRate
            );

        sum +=
            accrual
            *
            df;
    }

    return sum;
}

/*
    Forward swap rate:

        S(t) = [1 - P(t,T_N)] / A(t)
*/

double BermudanSwaption::forwardSwapRate(
    const HullWhiteModel& model,
    double exerciseTime,
    double shortRate
) const {

    std::vector<double> payDates =
        paymentDates(
            exerciseTime
        );

    if(payDates.empty()){
        return 0.0;
    }

    double finalMaturity =
        payDates.back();

    double finalDf =
        zeroCouponBondPrice(
            model,
            exerciseTime,
            finalMaturity,
            shortRate
        );

    double floatLeg =
        1.0
        -
        finalDf;

    double ann =
        annuity(
            model,
            exerciseTime,
            shortRate
        );

    if(std::abs(ann) < 1e-12){
        return 0.0;
    }

    return
        floatLeg
        /
        ann;
}

/*
    Payer swap:

        N * A(t) * [S(t) - K]

    Receiver swap:

        N * A(t) * [K - S(t)]
*/

double BermudanSwaption::swapValue(
    const HullWhiteModel& model,
    double exerciseTime,
    double shortRate
) const {

    double ann =
        annuity(
            model,
            exerciseTime,
            shortRate
        );

    double swapRate =
        forwardSwapRate(
            model,
            exerciseTime,
            shortRate
        );

    double value;

    if(payer){

        value =
            ann
            *
            (
                swapRate
                -
                fixedRate
            );

    } else {

        value =
            ann
            *
            (
                fixedRate
                -
                swapRate
            );
    }

    return
        notional
        *
        value;
}

/*
    Immediate exercise value:

        max(swap value, 0)
*/

double BermudanSwaption::exerciseValue(
    const HullWhiteModel& model,
    double exerciseTime,
    double shortRate
) const {

    return std::max(
        swapValue(
            model,
            exerciseTime,
            shortRate
        ),
        0.0
    );
}
