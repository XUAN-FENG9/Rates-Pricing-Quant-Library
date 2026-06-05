#include "VolSurface.hpp"

#include <stdexcept>
#include <algorithm>

/*
    Constructor
*/

VolSurface::VolSurface(
    const std::vector<double>& expiries_,
    const std::vector<double>& strikes_,
    const std::vector<std::vector<double>>& vols_
){

    expiries = expiries_;
    strikes = strikes_;
    vols = vols_;
}

/*
    Simple bilinear interpolation.

    NOTE:
    Python version uses LinearNDInterpolator.

    In C++ we implement explicit bilinear interpolation because:
    - standard C++ has no scipy equivalent
    - grid is rectangular
    - easier to debug and validate
*/

double VolSurface::getVol(
    double expiry,
    double strike
) const {

    if(
        expiry < expiries.front()
        || expiry > expiries.back()
        || strike < strikes.front()
        || strike > strikes.back()
    ){
        throw std::runtime_error(
            "VolSurface interpolation point outside grid."
        );
    }

    auto itT = std::upper_bound(
        expiries.begin(),
        expiries.end(),
        expiry
    );

    auto itK = std::upper_bound(
        strikes.begin(),
        strikes.end(),
        strike
    );

    int i = std::max(
        1,
        static_cast<int>(itT - expiries.begin())
    );

    int j = std::max(
        1,
        static_cast<int>(itK - strikes.begin())
    );

    if(i >= static_cast<int>(expiries.size())){
        i = expiries.size() - 1;
    }

    if(j >= static_cast<int>(strikes.size())){
        j = strikes.size() - 1;
    }

    double T1 = expiries[i - 1];
    double T2 = expiries[i];

    double K1 = strikes[j - 1];
    double K2 = strikes[j];

    double Q11 = vols[i - 1][j - 1];
    double Q12 = vols[i - 1][j];
    double Q21 = vols[i][j - 1];
    double Q22 = vols[i][j];

    double wtT = (expiry - T1) / (T2 - T1);
    double wtK = (strike - K1) / (K2 - K1);

    return
        (1.0 - wtT) * (1.0 - wtK) * Q11
        + (1.0 - wtT) * wtK * Q12
        + wtT * (1.0 - wtK) * Q21
        + wtT * wtK * Q22;
}
