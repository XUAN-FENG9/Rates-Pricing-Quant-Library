#ifndef TENORSTRUCTURE_HPP_INCLUDED
#define TENORSTRUCTURE_HPP_INCLUDED

#include <vector>

#include "ZeroCurve.hpp"

/*
    TenorStructure.hpp

    Discrete LMM tenor structure.

    Forward L_i applies to:

        [T_i, T_{i+1}]
*/

class TenorStructure {

private:

    double start_;
    double end_;

    int paymentFrequency_;

    std::vector<double> times_;
    std::vector<double> accruals_;

public:

    TenorStructure(
        double start,
        double end,
        int paymentFrequency = 2
    );

    int numberOfForwards() const;

    double start() const;

    double end() const;

    int paymentFrequency() const;

    const std::vector<double>& times() const;

    const std::vector<double>& accruals() const;

    std::vector<double> initialForwardRates(
        const ZeroCurve& curve
    ) const;

    std::vector<double> initialDiscountFactors(
        const ZeroCurve& curve
    ) const;

    int timeIndex(
        double targetTime,
        double tolerance = 1e-8
    ) const;

    int forwardIndex(
        double resetTime,
        double tolerance = 1e-8
    ) const;
};

#endif // TENORSTRUCTURE_HPP_INCLUDED
