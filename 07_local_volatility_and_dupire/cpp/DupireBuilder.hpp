#ifndef DUPIREBUILDER_HPP_INCLUDED
#define DUPIREBUILDER_HPP_INCLUDED

#include <vector>

#include "SwaptionPriceSurface.hpp"
#include "LocalVolSurface.hpp"

/*
    DupireBuilder

    Builds local volatility surface from option price surface:

        sigma_loc^2(K,T)
        =
        dC/dT
        /
        (0.5 * K^2 * d2C/dK2)
*/

class DupireBuilder {

public:

    SwaptionPriceSurface* priceSurface;

    DupireBuilder(
        SwaptionPriceSurface* priceSurface_
    );

    LocalVolSurface build();
};

#endif // DUPIREBUILDER_HPP_INCLUDED
