#include "LocalVolSurface.hpp"

#include <algorithm>
#include <stdexcept>
#include <cmath>

/*
    Constructor
*/

LocalVolSurface::LocalVolSurface(
    const std::vector<double>& expiries_,
    const std::vector<double>& strikes_,
    const std::vector<std::vector<double>>& localVols_
){

    expiries = expiries_;
    strikes = strikes_;
    localVols = localVols_;
}

/*
    Bilinear interpolation for local volatility.

    Boundary NaNs are expected because Dupire uses central differences.
    Therefore users should query inside the valid interior region.
*/

double LocalVolSurface::getLocalVol(
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
            "LocalVolSurface interpolation point outside grid."
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

    double Q11 = localVols[i - 1][j - 1];
    double Q12 = localVols[i - 1][j];
    double Q21 = localVols[i][j - 1];
    double Q22 = localVols[i][j];

    if(
        std::isnan(Q11)
        || std::isnan(Q12)
        || std::isnan(Q21)
        || std::isnan(Q22)
    ){
        throw std::runtime_error(
            "LocalVolSurface interpolation cell contains NaN."
        );
    }

    double wtT = (expiry - T1) / (T2 - T1);
    double wtK = (strike - K1) / (K2 - K1);

    return
        (1.0 - wtT) * (1.0 - wtK) * Q11
        + (1.0 - wtT) * wtK * Q12
        + wtT * (1.0 - wtK) * Q21
        + wtT * wtK * Q22;
}
