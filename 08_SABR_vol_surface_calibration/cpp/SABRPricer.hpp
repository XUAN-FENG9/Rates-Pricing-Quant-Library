#ifndef SABRPRICER_HPP_INCLUDED
#define SABRPRICER_HPP_INCLUDED

#include "SABRModel.hpp"

#include "curve.hpp"
#include "forward_swap.hpp"
#include "black_swaption.hpp"

class SABRPricer {

public:

    SABRModel model;

    SABRPricer(
        const SABRModel& model_
    );

    double sabrVol(
        YieldCurve& curve,
        double expiry,
        double tenor,
        double strike,
        double notional
    );

    double pricePayerSwaption(
        YieldCurve& curve,
        double expiry,
        double tenor,
        double strike,
        double notional
    );
};

#endif // SABRPRICER_HPP_INCLUDED
