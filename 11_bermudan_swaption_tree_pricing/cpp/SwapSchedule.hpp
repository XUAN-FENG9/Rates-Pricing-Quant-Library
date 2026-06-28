#ifndef SWAPSCHEDULE_HPP_INCLUDED
#define SWAPSCHEDULE_HPP_INCLUDED


#include <vector>

/*
    SwapSchedule.hpp

    Schedule utilities for Bermudan swaption pricing.
*/

std::vector<double> generatePaymentDates(
    double start,
    double end,
    int paymentFrequency = 2
);

std::vector<double> generateExerciseDates(
    double firstExercise,
    double lastExercise,
    int exerciseFrequency = 1
);

#endif // SWAPSCHEDULE_HPP_INCLUDED
