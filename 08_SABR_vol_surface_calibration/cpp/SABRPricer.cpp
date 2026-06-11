#include "SABRPricer.hpp"

SABRPricer::SABRPricer(
    const SABRModel& model_
)
: model(model_)
{
}

double SABRPricer::sabrVol(
    YieldCurve& curve,
    double expiry,
    double tenor,
    double strike,
    double notional
){
    ForwardStartingSwap swap(
        notional,
        // 0.0,
        expiry,
        expiry + tenor,
        2
    );

    double forward =
        swap.forward_swap_rate(
            curve
        );

    return model.blackVol(
        forward,
        strike,
        expiry
    );
}

double SABRPricer::pricePayerSwaption(
    YieldCurve& curve,
    double expiry,
    double tenor,
    double strike,
    double notional
){
    ForwardStartingSwap swap(
        notional,
        // 0.0,
        expiry,
        expiry + tenor,
        2
    );

    double forward =
        swap.forward_swap_rate(
            curve
        );

    double vol =
        model.blackVol(
            forward,
            strike,
            expiry
        );

    BlackSwaption swaption(
        notional,
        strike,
        expiry,
        vol,
        swap,
        true
    );

    return swaption.price(
        curve
    );
}
