#ifndef BONDPRICING_HPP_INCLUDED
#define BONDPRICING_HPP_INCLUDED

#include "HullWhiteModel.hpp"

/*
    BondPricing.hpp

    Zero-coupon bond pricing under Hull-White:

        P(t,T) = A(t,T) exp(-B(t,T) r(t))
*/

double AFunction(
    const HullWhiteModel& model,
    double t,
    double T
);

double zeroCouponBondPrice(
    const HullWhiteModel& model,
    double t,
    double T,
    double r
);

#endif // BONDPRICING_HPP_INCLUDED
