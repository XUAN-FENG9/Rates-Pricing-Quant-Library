#ifndef LSMBERMUDANPRICER_HPP_INCLUDED
#define LSMBERMUDANPRICER_HPP_INCLUDED

#include <vector>
#include <string>

#include "../../09_hull_white_short_rate_model/cpp/HullWhiteModel.hpp"
#include "../../11_bermudan_swaption_tree_pricing/cpp/BermudanSwaption.hpp"

#include "LSMPathSimulation.hpp"

/*
    Regression diagnostic result.
*/

struct RegressionDiagnostic {

    double exerciseTime;

    int numberOfRegressionPaths;

    std::vector<double> coefficients;
};

/*
    Longstaff-Schwartz Bermudan swaption pricer.
*/

class LSMBermudanPricer {

public:

    const HullWhiteModel* model;

    const BermudanSwaption* instrument;

    std::vector<double> times;

    std::vector<std::vector<double>> ratePaths;

    std::string basisType;

    int basisDegree;

    std::vector<int> exerciseIndices;

    std::vector<double> cashflows;

    std::vector<int> exerciseTimeIndex;

    std::vector<std::vector<bool>> exerciseFlagMatrix;

    std::vector<RegressionDiagnostic> regressionDiagnostics;

    LSMBermudanPricer(
        const HullWhiteModel* model_,
        const BermudanSwaption* instrument_,
        const std::vector<double>& times_,
        const std::vector<std::vector<double>>& ratePaths_,
        const std::string& basisType_ = "rate_swap",
        int basisDegree_ = 2
    );

    double discountBondPathwise(
        int startIndex,
        double endTime,
        int pathIndex
    ) const;

    void swapRateAndAnnuityPathwise(
        int exerciseIndex,
        int pathIndex,
        double& swapRate,
        double& annuity
    ) const;

    std::vector<double> immediateExerciseValues(
        int exerciseIndex,
        std::vector<double>& swapRates
    ) const;

    std::vector<double> solveLeastSquares(
        const std::vector<std::vector<double>>& X,
        const std::vector<double>& y
    ) const;

    double price();

    void printExerciseSummary() const;

    void printRegressionDiagnostics() const;
};

#endif // LSMBERMUDANPRICER_HPP_INCLUDED
