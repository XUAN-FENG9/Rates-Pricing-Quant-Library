#ifndef STOCHASTICVOLMODEL_HPP_INCLUDED
#define STOCHASTICVOLMODEL_HPP_INCLUDED

#include "HullWhiteModel.hpp"

/*
    StochasticVolModel.hpp

    Hull-White-style short-rate model with stochastic variance.

    Base Hull-White:

        dr_t = [theta(t) - a r_t] dt + sigma dW_t

    Stochastic-vol extension:

        dr_t = [theta(t) - a r_t] dt + sqrt(v_t) dW_t^r

        dv_t = kappa (v_bar - v_t) dt
               + eta sqrt(v_t) dW_t^v

    with:

        corr(dW_t^r, dW_t^v) = rho dt
*/

class StochasticVolModel {

public:

    HullWhiteModel* baseModel;

    double a;
    double kappa;
    double vBar;
    double eta;
    double rho;

    StochasticVolModel(
        HullWhiteModel* baseModel_,
        double kappa_,
        double vBar_,
        double eta_,
        double rho_
    );

    double theta(
        double t
    ) const;

    double shortRateDrift(
        double t,
        double r
    ) const;

    double varianceDrift(
        double v
    ) const;

    double instantaneousVolatility(
        double v
    ) const;

    void evolve(
        double t,
        double r,
        double v,
        double dt,
        double zRate,
        double zVol,
        double& rNext,
        double& vNext
    ) const;
};

#endif // STOCHASTICVOLMODEL_HPP_INCLUDED
