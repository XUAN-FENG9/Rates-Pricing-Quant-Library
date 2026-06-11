#include <iostream>
#include <vector>
#include <iomanip>
#include <cmath>

#include "curve.hpp"
#include "forward_swap.hpp"
#include "black_swaption.hpp"

#include "SABRModel.hpp"
#include "SABRCalibration.hpp"
#include "SABRPricer.hpp"

int main(){

    /*
        1. Build yield curve.

        Same curve convention as Chapter 07 / 08 curve_data.csv.
    */

    std::vector<double> maturities = {
        0.0833, 0.1667, 0.25, 0.5, 0.75,
        1.0, 1.5, 2.0, 2.5, 3.0,
        3.5, 4.0, 4.5, 5.0, 6.0,
        7.0, 8.0, 9.0, 10.0, 12.0,
        15.0, 20.0, 25.0, 30.0
    };

    std::vector<double> zeroRates = {
        0.0452, 0.0453, 0.0454, 0.0456, 0.0457,
        0.0458, 0.0459, 0.0458, 0.0457, 0.0455,
        0.0453, 0.0451, 0.0449, 0.0447, 0.0444,
        0.0441, 0.0439, 0.0437, 0.0435, 0.0432,
        0.0429, 0.0426, 0.0424, 0.0422
    };

    YieldCurve curve(
        maturities,
        zeroRates
    );

    /*
        2. Example calibration slice: 5Y x 5Y swaption smile.

        Market vols are decimal Black vols.

        Example:
            0.255 = 25.5%
    */

    double expiry = 5.0;
    double tenor = 5.0;
    double notional = 1000000.0;

    ForwardStartingSwap swap(
        notional,
        // 0.0,
        expiry,
        expiry + tenor,
        2
    );

    double forward =
        swap.forward_swap_rate(
            curve
        );

    std::vector<double> strikeShiftsBp = {
        -300, -250, -200, -150, -100, -50,
        0,
        50, 100, 150, 200, 250, 300
    };

    /*
        5Y row from the improved market surface after scaling:

        Original values:
            76,69,64,60,57,54,51,53,55,58,62,67,73

        Scaled by 50:
            3800,3450,...,2550,...

        Decimal Black vols:
            /10000
    */

    std::vector<double> marketVols = {
        0.3800, 0.3450, 0.3200, 0.3000, 0.2850, 0.2700,
        0.2550,
        0.2650, 0.2750, 0.2900, 0.3100, 0.3350, 0.3650
    };

    std::vector<double> strikes;

    for(double shift : strikeShiftsBp){

        double K =
            forward
            +
            shift / 10000.0;

        strikes.push_back(K);
    }

    std::cout
        << std::fixed
        << std::setprecision(6);

    std::cout
        << "Forward swap rate: "
        << forward
        << std::endl;

    /*
        3. SABR calibration.

        We fix beta = 0.5 and calibrate:

            alpha, rho, nu

        Initial guess follows Python logic.
    */

    double beta = 0.5;

    double atmVol = marketVols[6];

    double initialAlpha =
        atmVol
        *
        std::pow(
            forward,
            1.0 - beta
        );

    double initialRho = 0.30;
    double initialNu = 0.50;

    SABRCalibrationResult calib =
        SABRCalibration::calibrateSlice(
            forward,
            expiry,
            strikes,
            marketVols,
            beta,
            initialAlpha,
            initialRho,
            initialNu
        );

    std::cout
        << "\nSABR Calibration Result"
        << std::endl;

    std::cout
        << "alpha = "
        << calib.alpha
        << std::endl;

    std::cout
        << "beta  = "
        << calib.beta
        << std::endl;

    std::cout
        << "rho   = "
        << calib.rho
        << std::endl;

    std::cout
        << "nu    = "
        << calib.nu
        << std::endl;

    std::cout
        << "RMSE  = "
        << calib.rmse
        << std::endl;

    /*
        4. Print market vs fitted smile.
    */

    SABRModel calibratedModel(
        calib.alpha,
        calib.beta,
        calib.rho,
        calib.nu
    );

    std::cout
        << "\nStrike Shift, Strike, Market Vol, SABR Vol, Error"
        << std::endl;

    for(size_t i = 0; i < strikes.size(); ++i){

        double modelVol =
            calibratedModel.blackVol(
                forward,
                strikes[i],
                expiry
            );

        std::cout
            << strikeShiftsBp[i]
            << ", "
            << strikes[i]
            << ", "
            << marketVols[i]
            << ", "
            << modelVol
            << ", "
            << modelVol - marketVols[i]
            << std::endl;
    }

    /*
        5. Price ATM payer swaption using calibrated SABR vol.
    */

    SABRPricer pricer(
        calibratedModel
    );

    double atmStrike =
        forward;

    double atmSabrVol =
        pricer.sabrVol(
            curve,
            expiry,
            tenor,
            atmStrike,
            notional
        );

    double atmPrice =
        pricer.pricePayerSwaption(
            curve,
            expiry,
            tenor,
            atmStrike,
            notional
        );

    std::cout
        << "\nATM SABR vol: "
        << atmSabrVol
        << std::endl;

    std::cout
        << "ATM SABR payer swaption price: "
        << atmPrice
        << std::endl;

    /*
        6. Compare with flat Black price.
    */

    BlackSwaption flatBlack(
        notional,
        atmStrike,
        expiry,
        0.2550,
        swap,
        true
    );

    double flatPrice =
        flatBlack.price(
            curve
        );

    std::cout
        << "Flat Black ATM price: "
        << flatPrice
        << std::endl;

    return 0;
}
