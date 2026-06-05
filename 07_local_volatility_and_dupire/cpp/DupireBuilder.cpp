#include "DupireBuilder.hpp"

#include <cmath>
#include <limits>

/*
    Constructor
*/

DupireBuilder::DupireBuilder(
    SwaptionPriceSurface* priceSurface_
){

    priceSurface = priceSurface_;
}

/*
    Build Dupire local volatility surface.

    Boundary rows/columns are set to NaN because central finite
    differences require neighboring expiry and strike points.
*/

LocalVolSurface DupireBuilder::build(){

    std::vector<double> expiries =
        priceSurface->expiries;

    std::vector<double> strikes =
        priceSurface->strikes;

    std::vector<std::vector<double>> prices =
        priceSurface->prices;

    size_t nT = expiries.size();
    size_t nK = strikes.size();

    double NaN =
        std::numeric_limits<double>::quiet_NaN();

    std::vector<std::vector<double>> localVols(
        nT,
        std::vector<double>(nK, NaN)
    );

    for(size_t i = 1; i < nT - 1; ++i){

        for(size_t j = 1; j < nK - 1; ++j){

            double TPrev = expiries[i - 1];
            double TNext = expiries[i + 1];

            double KPrev = strikes[j - 1];
            double K = strikes[j];
            double KNext = strikes[j + 1];

            double C_TPrev = prices[i - 1][j];
            double C_TNext = prices[i + 1][j];

            double C_KPrev = prices[i][j - 1];
            double C_K = prices[i][j];
            double C_KNext = prices[i][j + 1];

            double dCdT =
                (C_TNext - C_TPrev)
                /
                (TNext - TPrev);

            double dKLeft = K - KPrev;
            double dKRight = KNext - K;

            if(std::abs(dKLeft - dKRight) > 1e-10){
                continue;
            }

            double dK = dKLeft;

            double d2CdK2 =
                (
                    C_KNext
                    - 2.0 * C_K
                    + C_KPrev
                )
                /
                (dK * dK);

            double denominator =
                0.5
                * K
                * K
                * d2CdK2;

            if(dCdT <= 0.0 || denominator <= 0.0){
                continue;
            }

            double localVar =
                dCdT / denominator;

            if(localVar <= 0.0){
                continue;
            }

            localVols[i][j] =
                std::sqrt(localVar);
        }
    }

    return LocalVolSurface(
        expiries,
        strikes,
        localVols
    );
}
