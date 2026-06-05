#ifndef LOCALVOLSURFACE_HPP_INCLUDED
#define LOCALVOLSURFACE_HPP_INCLUDED

#include <vector>

/*
    LocalVolSurface

    Stores Dupire local volatility surface:

        sigma_local(expiry, strike)

    This is model-implied, not directly market quoted.
*/

class LocalVolSurface {

public:

    std::vector<double> expiries;
    std::vector<double> strikes;
    std::vector<std::vector<double>> localVols;

    LocalVolSurface(
        const std::vector<double>& expiries_,
        const std::vector<double>& strikes_,
        const std::vector<std::vector<double>>& localVols_
    );

    double getLocalVol(
        double expiry,
        double strike
    ) const;
};

#endif // LOCALVOLSURFACE_HPP_INCLUDED
