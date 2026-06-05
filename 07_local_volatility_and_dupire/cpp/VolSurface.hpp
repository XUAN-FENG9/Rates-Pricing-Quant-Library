#ifndef VOLSURFACE_HPP_INCLUDED
#define VOLSURFACE_HPP_INCLUDED

#include <vector>

/*
    VolSurface

    Stores Black implied volatility surface:

        sigma_imp(expiry, strike)

    This is the C++ equivalent of python/vol_surface.py.

    Inputs are already cleaned:
    - expiry in years
    - strike as actual rate level
    - volatility in decimal form
*/

class VolSurface {

public:

    std::vector<double> expiries;
    std::vector<double> strikes;
    std::vector<std::vector<double>> vols;

    VolSurface(
        const std::vector<double>& expiries_,
        const std::vector<double>& strikes_,
        const std::vector<std::vector<double>>& vols_
    );

    double getVol(
        double expiry,
        double strike
    ) const;
};

#endif // VOLSURFACE_HPP_INCLUDED
