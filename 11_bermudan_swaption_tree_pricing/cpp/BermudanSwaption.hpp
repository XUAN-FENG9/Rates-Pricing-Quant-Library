#ifndef BERMUDANSWAPTION_HPP_INCLUDED
#define BERMUDANSWAPTION_HPP_INCLUDED

#include <vector>
#include <map>

#include "SwapSchedule.hpp"

#include "HullWhiteModel.hpp"

/*
    BermudanSwaption.hpp

    Market-style Bermudan swaption definition:

        exercise at time t
            ¡õ
        enter into swap starting at t
            ¡õ
        swap ends at t + swapTenor
*/

class BermudanSwaption {

public:

    double notional;
    double fixedRate;

    double optionStart;
    double optionEnd;
    double swapTenor;

    int paymentFrequency;
    int exerciseFrequency;

    bool payer;

    std::vector<double> exerciseDates;

    std::map<double, std::vector<double>> paymentScheduleCache;

    BermudanSwaption(
        double notional_,
        double fixedRate_,
        double optionStart_,
        double optionEnd_,
        double swapTenor_,
        int paymentFrequency_ = 2,
        int exerciseFrequency_ = 1,
        bool payer_ = true
    );

    std::vector<double> paymentDates(
        double exerciseTime
    ) const;

    double annuity(
        const HullWhiteModel& model,
        double exerciseTime,
        double shortRate
    ) const;

    double forwardSwapRate(
        const HullWhiteModel& model,
        double exerciseTime,
        double shortRate
    ) const;

    double swapValue(
        const HullWhiteModel& model,
        double exerciseTime,
        double shortRate
    ) const;

    double exerciseValue(
        const HullWhiteModel& model,
        double exerciseTime,
        double shortRate
    ) const;
};

#endif // BERMUDANSWAPTION_HPP_INCLUDED
