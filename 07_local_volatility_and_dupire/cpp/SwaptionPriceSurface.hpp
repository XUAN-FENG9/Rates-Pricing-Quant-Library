#ifndef SWAPTIONPRICESURFACE_H_INCLUDED
#define SWAPTIONPRICESURFACE_H_INCLUDED

#include <vector>

#include "VolSurface.hpp"

// Import Chapter 06 components
#include "curve.hpp"
#include "forward_swap.hpp"
#include "black_swaption.hpp"

/*
    SwaptionPriceSurface

    Builds Black swaption price surface:

        C(expiry, strike)

    using:
    - YieldCurve
    - ForwardStartingSwap
    - BlackSwaption
    - VolSurface
*/

class SwaptionPriceSurface {

public:

    YieldCurve* curve;
    VolSurface* volSurface;

    double tenor;
    double notional;
    bool payer;

    std::vector<double> expiries;
    std::vector<double> strikes;

    std::vector<std::vector<double>> prices;

    SwaptionPriceSurface(
        YieldCurve* curve_,
        VolSurface* volSurface_,
        double tenor_,
        double notional_,
        bool payer_
    );

    std::vector<std::vector<double>> build();
};

#endif // SWAPTIONPRICESURFACE_H_INCLUDED
