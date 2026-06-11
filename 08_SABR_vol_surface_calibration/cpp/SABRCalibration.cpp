#include "SABRCalibration.hpp"
#include "SABRModel.hpp"

#include <cmath>
#include <algorithm>
#include <iostream>

double SABRCalibration::objective(
    double alpha,
    double rho,
    double nu,
    double beta,
    double forward,
    double expiry,
    const std::vector<double>& strikes,
    const std::vector<double>& marketVols
){
    /*
        Parameter constraints.

        These bounds mirror the stabilized Python calibration:

        alpha > 0
        rho in [-0.90, 0.90]
        nu  in [0.05, 2.0]
    */

    if(alpha <= 0.0){
        return 1e10;
    }

    if(rho <= -0.90 || rho >= 0.90){
        return 1e10;
    }

    if(nu < 0.05 || nu > 2.0){
        return 1e10;
    }

    SABRModel model(
        alpha,
        beta,
        rho,
        nu
    );

    double error = 0.0;

    try {

        for(size_t i = 0; i < strikes.size(); ++i){

            double modelVol =
                model.blackVol(
                    forward,
                    strikes[i],
                    expiry
                );

            double diff =
                modelVol
                - marketVols[i];

            error += diff * diff;
        }

    } catch(...){

        return 1e10;
    }

    return error;
}

SABRCalibrationResult SABRCalibration::calibrateSlice(
    double forward,
    double expiry,
    const std::vector<double>& strikes,
    const std::vector<double>& marketVols,
    double beta,
    double initialAlpha,
    double initialRho,
    double initialNu
){
    /*
        Simple coordinate-search optimizer.

        This avoids external dependencies and is sufficient
        for a GitHub educational C++ demo.

        In production, this would usually be replaced by:
        - Levenberg-Marquardt
        - BFGS / L-BFGS-B
        - QuantLib optimizer
        - internal desk optimizer
    */

    double alpha = initialAlpha;
    double rho = initialRho;
    double nu = initialNu;

    double stepAlpha = 0.005;
    double stepRho = 0.05;
    double stepNu = 0.05;

    double bestObj =
        objective(
            alpha,
            rho,
            nu,
            beta,
            forward,
            expiry,
            strikes,
            marketVols
        );

    int maxIter = 2000;

    for(int iter = 0; iter < maxIter; ++iter){

        bool improved = false;

        std::vector<std::vector<double>> candidates = {
            {alpha + stepAlpha, rho, nu},
            {alpha - stepAlpha, rho, nu},
            {alpha, rho + stepRho, nu},
            {alpha, rho - stepRho, nu},
            {alpha, rho, nu + stepNu},
            {alpha, rho, nu - stepNu}
        };

        for(const auto& c : candidates){

            double a = c[0];
            double r = c[1];
            double n = c[2];

            double obj =
                objective(
                    a,
                    r,
                    n,
                    beta,
                    forward,
                    expiry,
                    strikes,
                    marketVols
                );

            if(obj < bestObj){

                bestObj = obj;
                alpha = a;
                rho = r;
                nu = n;
                improved = true;
            }
        }

        if(!improved){

            stepAlpha *= 0.7;
            stepRho *= 0.7;
            stepNu *= 0.7;
        }

        if(
            stepAlpha < 1e-8
            && stepRho < 1e-6
            && stepNu < 1e-6
        ){
            break;
        }
    }

    double rmse =
        std::sqrt(
            bestObj / strikes.size()
        );

    SABRCalibrationResult result;

    result.alpha = alpha;
    result.beta = beta;
    result.rho = rho;
    result.nu = nu;
    result.objective = bestObj;
    result.rmse = rmse;
    result.success = true;

    return result;
}
