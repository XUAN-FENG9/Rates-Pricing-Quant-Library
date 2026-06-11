#ifndef SABRCALIBRATION_HPP_INCLUDED
#define SABRCALIBRATION_HPP_INCLUDED

#include <vector>

struct SABRCalibrationResult {

    double alpha;
    double beta;
    double rho;
    double nu;

    double rmse;
    double objective;

    bool success;
};

class SABRCalibration {

public:

    static double objective(
        double alpha,
        double rho,
        double nu,
        double beta,
        double forward,
        double expiry,
        const std::vector<double>& strikes,
        const std::vector<double>& marketVols
    );

    static SABRCalibrationResult calibrateSlice(
        double forward,
        double expiry,
        const std::vector<double>& strikes,
        const std::vector<double>& marketVols,
        double beta,
        double initialAlpha,
        double initialRho,
        double initialNu
    );
};

#endif // SABRCALIBRATION_HPP_INCLUDED
