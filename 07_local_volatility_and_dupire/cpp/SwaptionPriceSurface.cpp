#include "SwaptionPriceSurface.hpp"

/*
    Constructor
*/

SwaptionPriceSurface::SwaptionPriceSurface(
    YieldCurve* curve_,
    VolSurface* volSurface_,
    double tenor_,
    double notional_,
    bool payer_
){

    curve = curve_;
    volSurface = volSurface_;

    tenor = tenor_;
    notional = notional_;
    payer = payer_;

    expiries = volSurface->expiries;
    strikes = volSurface->strikes;
}

/*
    Build Black swaption price matrix.

    For each expiry:
    - construct forward-starting swap
    - read Black vol from implied vol surface
    - price payer/receiver swaption using Chapter 06 BlackSwaption
*/

std::vector<std::vector<double>>
SwaptionPriceSurface::build(){

    prices = std::vector<std::vector<double>>(
        expiries.size(),
        std::vector<double>(strikes.size(), 0.0)
    );

    for(size_t i = 0; i < expiries.size(); ++i){

        double expiry = expiries[i];

        ForwardStartingSwap underlyingSwap(
            notional,
            //0.0,                 // fixed rate not needed for forward swap rate
            expiry,
            expiry + tenor,
            2
        );

        for(size_t j = 0; j < strikes.size(); ++j){

            double strike = strikes[j];

            double vol = volSurface->getVol(
                expiry,
                strike
            );

            BlackSwaption swaption(
                notional,
                strike,
                expiry,
                vol,
                underlyingSwap,
                payer
            );

            prices[i][j] = swaption.price(
                *curve
            );
        }
    }

    return prices;
}
