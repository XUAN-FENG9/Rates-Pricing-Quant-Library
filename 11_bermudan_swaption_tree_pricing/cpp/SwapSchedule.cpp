#include "SwapSchedule.hpp"

#include <cmath>

/*
    Generate regular fixed-leg payment dates.

    Example:
        start = 2.0
        end   = 7.0
        paymentFrequency = 2

    returns:
        2.5, 3.0, 3.5, ..., 7.0
*/

std::vector<double> generatePaymentDates(
    double start,
    double end,
    int paymentFrequency
){

    double dt =
        1.0
        /
        static_cast<double>(
            paymentFrequency
        );

    int nPayments =
        static_cast<int>(
            std::round(
                (end - start)
                *
                paymentFrequency
            )
        );

    std::vector<double> dates;

    for(int i = 0; i < nPayments; ++i){

        dates.push_back(
            start
            +
            (i + 1)
            *
            dt
        );
    }

    return dates;
}

/*
    Generate Bermudan exercise dates.
*/

std::vector<double> generateExerciseDates(
    double firstExercise,
    double lastExercise,
    int exerciseFrequency
){

    double dt =
        1.0
        /
        static_cast<double>(
            exerciseFrequency
        );

    int nDates =
        static_cast<int>(
            std::round(
                (lastExercise - firstExercise)
                *
                exerciseFrequency
            )
        );

    std::vector<double> dates;

    for(int i = 0; i <= nDates; ++i){

        dates.push_back(
            firstExercise
            +
            i
            *
            dt
        );
    }

    return dates;
}
