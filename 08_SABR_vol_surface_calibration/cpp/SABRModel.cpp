#include "SABRModel.hpp"

#include <cmath>
#include <stdexcept>

SABRModel::SABRModel(
    double alpha_,
    double beta_,
    double rho_,
    double nu_
){
    alpha = alpha_;
    beta = beta_;
    rho = rho_;
    nu = nu_;
}

double SABRModel::blackVol(
    double forward,
    double strike,
    double expiry
) const {

    double F = forward;
    double K = strike;
    double T = expiry;

    if(F <= 0.0 || K <= 0.0){
        throw std::runtime_error(
            "SABR Black formula requires positive forward and strike."
        );
    }

    double oneMinusBeta = 1.0 - beta;

    if(std::abs(F - K) < 1e-12){

        double FKbeta =
            std::pow(F, oneMinusBeta);

        double term1 =
            oneMinusBeta * oneMinusBeta / 24.0
            * alpha * alpha
            / std::pow(F, 2.0 * oneMinusBeta);

        double term2 =
            0.25
            * rho
            * beta
            * nu
            * alpha
            / std::pow(F, oneMinusBeta);

        double term3 =
            (2.0 - 3.0 * rho * rho)
            * nu * nu
            / 24.0;

        return
            alpha / FKbeta
            * (1.0 + (term1 + term2 + term3) * T);
    }

    double logFK = std::log(F / K);
    double FK = F * K;

    double FKbeta =
        std::pow(
            FK,
            oneMinusBeta / 2.0
        );

    double z =
        (nu / alpha)
        * FKbeta
        * logFK;

    double xz =
        std::log(
            (
                std::sqrt(
                    1.0 - 2.0 * rho * z + z * z
                )
                + z
                - rho
            )
            /
            (1.0 - rho)
        );

    double denominator =
        FKbeta
        *
        (
            1.0
            + oneMinusBeta * oneMinusBeta / 24.0 * logFK * logFK
            + std::pow(oneMinusBeta, 4.0) / 1920.0 * std::pow(logFK, 4.0)
        );

    double term1 =
        oneMinusBeta * oneMinusBeta / 24.0
        * alpha * alpha
        / std::pow(FK, oneMinusBeta);

    double term2 =
        0.25
        * rho
        * beta
        * nu
        * alpha
        / std::pow(FK, oneMinusBeta / 2.0);

    double term3 =
        (2.0 - 3.0 * rho * rho)
        * nu * nu
        / 24.0;

    return
        alpha
        / denominator
        * (z / xz)
        * (1.0 + (term1 + term2 + term3) * T);
}

std::vector<double> SABRModel::blackVolVector(
    double forward,
    const std::vector<double>& strikes,
    double expiry
) const {

    std::vector<double> vols;

    for(double K : strikes){
        vols.push_back(
            blackVol(
                forward,
                K,
                expiry
            )
        );
    }

    return vols;
}
