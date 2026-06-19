#ifndef BONDOPTIONPRICING_HPP_INCLUDED
#define BONDOPTIONPRICING_HPP_INCLUDED

#include "HullWhiteModel.hpp"
#include "HullWhiteSimulation.hpp"

/*
    BondOptionPricing.hpp

    European option on a zero-coupon bond under Hull-White.
*/

double normalCDF(
    double x
);

double bondOptionVolatility(
    const HullWhiteModel& model,
    double optionExpiry,
    double bondMaturity
);

double priceZeroCouponBondOption(
    const HullWhiteModel& model,
    double optionExpiry,
    double bondMaturity,
    double strike,
    bool isCall = true
);

double monteCarloBondOptionPrice(
    const HullWhiteModel& model,
    const SimulationResult& result,
    double optionExpiry,
    double bondMaturity,
    double strike,
    bool isCall = true
);

#endif // BONDOPTIONPRICING_HPP_INCLUDED
