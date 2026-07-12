#include "TenorStructure.hpp"

#include <cmath>
#include <limits>
#include <stdexcept>

/*
    Constructor.
*/

TenorStructure::TenorStructure(
    double start,
    double end,
    int paymentFrequency
)
    :
    start_(start),
    end_(end),
    paymentFrequency_(paymentFrequency)
{

    if(end_ <= start_){

        throw std::invalid_argument(
            "Tenor end must be greater than tenor start."
        );
    }

    if(paymentFrequency_ <= 0){

        throw std::invalid_argument(
            "Payment frequency must be positive."
        );
    }

    double delta =
        1.0
        /
        static_cast<double>(
            paymentFrequency_
        );

    int numberOfPeriods =
        static_cast<int>(
            std::round(
                (end_ - start_)
                *
                paymentFrequency_
            )
        );

    times_.resize(
        numberOfPeriods + 1
    );

    accruals_.resize(
        numberOfPeriods
    );

    for(int i = 0; i <= numberOfPeriods; ++i){

        times_[i] =
            start_
            +
            i
            *
            delta;
    }

    for(int i = 0; i < numberOfPeriods; ++i){

        accruals_[i] =
            times_[i + 1]
            -
            times_[i];
    }
}

int TenorStructure::numberOfForwards() const {

    return static_cast<int>(
        accruals_.size()
    );
}

double TenorStructure::start() const {

    return start_;
}

double TenorStructure::end() const {

    return end_;
}

int TenorStructure::paymentFrequency() const {

    return paymentFrequency_;
}

const std::vector<double>& TenorStructure::times() const {

    return times_;
}

const std::vector<double>& TenorStructure::accruals() const {

    return accruals_;
}

/*
    Construct initial simple forward rates:

        L_i(0)
        =
        [P(0,T_i)/P(0,T_{i+1}) - 1]
        /
        delta_i
*/

std::vector<double> TenorStructure::initialForwardRates(
    const ZeroCurve& curve
) const {

    std::vector<double> forwards(
        numberOfForwards(),
        0.0
    );

    for(int i = 0; i < numberOfForwards(); ++i){

        double p0 =
            curve.discountFactor(
                times_[i]
            );

        double p1 =
            curve.discountFactor(
                times_[i + 1]
            );

        forwards[i] =
            (
                p0 / p1
                -
                1.0
            )
            /
            accruals_[i];
    }

    return forwards;
}

std::vector<double> TenorStructure::initialDiscountFactors(
    const ZeroCurve& curve
) const {

    std::vector<double> discountFactors;

    discountFactors.reserve(
        times_.size()
    );

    for(double time : times_){

        discountFactors.push_back(
            curve.discountFactor(
                time
            )
        );
    }

    return discountFactors;
}

int TenorStructure::timeIndex(
    double targetTime,
    double tolerance
) const {

    int bestIndex =
        0;

    double smallestDifference =
        std::numeric_limits<double>::max();

    for(std::size_t i = 0; i < times_.size(); ++i){

        double difference =
            std::abs(
                times_[i]
                -
                targetTime
            );

        if(difference < smallestDifference){

            smallestDifference =
                difference;

            bestIndex =
                static_cast<int>(i);
        }
    }

    if(smallestDifference > tolerance){

        throw std::invalid_argument(
            "Target time is not on the tenor grid."
        );
    }

    return bestIndex;
}

int TenorStructure::forwardIndex(
    double resetTime,
    double tolerance
) const {

    int index =
        timeIndex(
            resetTime,
            tolerance
        );

    if(index >= numberOfForwards()){

        throw std::invalid_argument(
            "Reset time does not correspond to an active forward."
        );
    }

    return index;
}
