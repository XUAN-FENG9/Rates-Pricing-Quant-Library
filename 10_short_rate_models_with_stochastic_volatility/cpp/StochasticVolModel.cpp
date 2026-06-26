#include "StochasticVolModel.hpp"

#include <cmath>
#include <stdexcept>
#include <algorithm>

/*
    Constructor
*/

StochasticVolModel::StochasticVolModel(
    HullWhiteModel* baseModel_,
    double kappa_,
    double vBar_,
    double eta_,
    double rho_
){
    baseModel = baseModel_;
    a = baseModel_->a;

    kappa = kappa_;
    vBar = vBar_;
    eta = eta_;
    rho = rho_;

    if(kappa <= 0.0){
        throw std::runtime_error("kappa must be positive.");
    }

    if(vBar <= 0.0){
        throw std::runtime_error("vBar must be positive.");
    }

    if(eta < 0.0){
        throw std::runtime_error("eta must be non-negative.");
    }

    if(rho <= -1.0 || rho >= 1.0){
        throw std::runtime_error("rho must be between -1 and 1.");
    }
}

/*
    Reuse theta(t) from Chapter 09 Hull-White model.
*/

double StochasticVolModel::theta(
    double t
) const {

    return baseModel->theta(t);
}

/*
    Short-rate drift:

        theta(t) - a r_t
*/

double StochasticVolModel::shortRateDrift(
    double t,
    double r
) const {

    return
        theta(t)
        -
        a * r;
}

/*
    Variance drift:

        kappa (vBar - v_t)
*/

double StochasticVolModel::varianceDrift(
    double v
) const {

    return
        kappa
        *
        (vBar - v);
}

/*
    Instantaneous volatility:

        sqrt(max(v,0))
*/

double StochasticVolModel::instantaneousVolatility(
    double v
) const {

    return
        std::sqrt(
            std::max(
                v,
                0.0
            )
        );
}

/*
    One Euler step with full truncation.

    v_pos = max(v,0)

    r_{t+dt}
        =
        r_t
        +
        [theta(t) - a r_t] dt
        +
        sqrt(v_pos) sqrt(dt) Z_r

    v_{t+dt}
        =
        v_t
        +
        kappa(vBar - v_pos) dt
        +
        eta sqrt(v_pos) sqrt(dt) Z_v
*/

void StochasticVolModel::evolve(
    double t,
    double r,
    double v,
    double dt,
    double zRate,
    double zVol,
    double& rNext,
    double& vNext
) const {

    double vPos =
        std::max(
            v,
            0.0
        );

    rNext =
        r
        +
        shortRateDrift(t, r) * dt
        +
        std::sqrt(vPos)
        *
        std::sqrt(dt)
        *
        zRate;

    vNext =
        v
        +
        varianceDrift(vPos) * dt
        +
        eta
        *
        std::sqrt(vPos)
        *
        std::sqrt(dt)
        *
        zVol;

    vNext =
        std::max(
            vNext,
            0.0
        );
}
