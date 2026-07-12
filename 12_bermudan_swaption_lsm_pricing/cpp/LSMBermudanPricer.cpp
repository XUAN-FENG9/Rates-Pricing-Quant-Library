#include "LSMBermudanPricer.hpp"
#include "RegressionBasis.hpp"

#include <cmath>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <stdexcept>

/*
    Constructor.
*/

LSMBermudanPricer::LSMBermudanPricer(
    const HullWhiteModel* model_,
    const BermudanSwaption* instrument_,
    const std::vector<double>& times_,
    const std::vector<std::vector<double>>& ratePaths_,
    const std::string& basisType_,
    int basisDegree_
){

    model = model_;
    instrument = instrument_;

    times = times_;
    ratePaths = ratePaths_;

    basisType = basisType_;
    basisDegree = basisDegree_;

    for(double t : instrument->exerciseDates){

        exerciseIndices.push_back(
            nearestTimeIndex(
                times,
                t
            )
        );
    }

    std::sort(
        exerciseIndices.begin(),
        exerciseIndices.end()
    );

    exerciseIndices.erase(
        std::unique(
            exerciseIndices.begin(),
            exerciseIndices.end()
        ),
        exerciseIndices.end()
    );
}

/*
    Pathwise discount bond P(t,T).
*/

double LSMBermudanPricer::discountBondPathwise(
    int startIndex,
    double endTime,
    int pathIndex
) const {

    int endIndex =
        nearestTimeIndex(
            times,
            endTime
        );

    if(endIndex <= startIndex){
        return 1.0;
    }

    return pathDiscountFactorBetweenIndices(
        times,
        ratePaths[pathIndex],
        startIndex,
        endIndex
    );
}

/*
    Pathwise forward swap rate and annuity.
*/

void LSMBermudanPricer::swapRateAndAnnuityPathwise(
    int exerciseIndex,
    int pathIndex,
    double& swapRate,
    double& annuity
) const {

    double exerciseTime =
        times[exerciseIndex];

    std::vector<double> payDates =
        instrument->paymentDates(
            exerciseTime
        );

    double accrual =
        1.0
        /
        static_cast<double>(
            instrument->paymentFrequency
        );

    annuity = 0.0;

    std::vector<double> dfs;

    for(double T : payDates){

        double df =
            discountBondPathwise(
                exerciseIndex,
                T,
                pathIndex
            );

        dfs.push_back(df);

        annuity +=
            accrual
            *
            df;
    }

    if(dfs.empty() || std::abs(annuity) < 1e-12){

        swapRate = 0.0;
        return;
    }

    double floatLeg =
        1.0
        -
        dfs.back();

    swapRate =
        floatLeg
        /
        annuity;
}

/*
    Immediate exercise values across all paths.
*/

std::vector<double> LSMBermudanPricer::immediateExerciseValues(
    int exerciseIndex,
    std::vector<double>& swapRates
) const {

    int nPaths =
        static_cast<int>(
            ratePaths.size()
        );

    std::vector<double> values(
        nPaths,
        0.0
    );

    swapRates =
        std::vector<double>(
            nPaths,
            0.0
        );

    for(int path = 0; path < nPaths; ++path){

        double swapRate;
        double annuity;

        swapRateAndAnnuityPathwise(
            exerciseIndex,
            path,
            swapRate,
            annuity
        );

        swapRates[path] =
            swapRate;

        double swapValue;

        if(instrument->payer){

            swapValue =
                instrument->notional
                *
                annuity
                *
                (
                    swapRate
                    -
                    instrument->fixedRate
                );

        } else {

            swapValue =
                instrument->notional
                *
                annuity
                *
                (
                    instrument->fixedRate
                    -
                    swapRate
                );
        }

        values[path] =
            std::max(
                swapValue,
                0.0
            );
    }

    return values;
}

/*
    Solve least squares by normal equations:

        beta = (X'X)^(-1) X'y

    This is simple and dependency-free.
    For production use, prefer QR decomposition.
*/

std::vector<double> LSMBermudanPricer::solveLeastSquares(
    const std::vector<std::vector<double>>& X,
    const std::vector<double>& y
) const {

    int n =
        static_cast<int>(
            X.size()
        );

    int k =
        static_cast<int>(
            X[0].size()
        );

    std::vector<std::vector<double>> A(
        k,
        std::vector<double>(
            k,
            0.0
        )
    );

    std::vector<double> b(
        k,
        0.0
    );

    for(int i = 0; i < n; ++i){

        for(int col = 0; col < k; ++col){

            b[col] +=
                X[i][col]
                *
                y[i];

            for(int row = 0; row < k; ++row){

                A[col][row] +=
                    X[i][col]
                    *
                    X[i][row];
            }
        }
    }

    /*
        Gaussian elimination with partial pivoting.
    */

    for(int i = 0; i < k; ++i){

        int pivot =
            i;

        for(int row = i + 1; row < k; ++row){

            if(std::abs(A[row][i]) > std::abs(A[pivot][i])){

                pivot =
                    row;
            }
        }

        std::swap(
            A[i],
            A[pivot]
        );

        std::swap(
            b[i],
            b[pivot]
        );

        double diag =
            A[i][i];

        if(std::abs(diag) < 1e-12){

            diag =
                1e-12;
        }

        for(int col = i; col < k; ++col){

            A[i][col] /=
                diag;
        }

        b[i] /=
            diag;

        for(int row = 0; row < k; ++row){

            if(row == i){
                continue;
            }

            double factor =
                A[row][i];

            for(int col = i; col < k; ++col){

                A[row][col] -=
                    factor
                    *
                    A[i][col];
            }

            b[row] -=
                factor
                *
                b[i];
        }
    }

    return b;
}

/*
    LSM price.
*/

double LSMBermudanPricer::price(){

    int nPaths =
        static_cast<int>(
            ratePaths.size()
        );

    int nSteps =
        static_cast<int>(
            times.size()
        );

    cashflows =
        std::vector<double>(
            nPaths,
            0.0
        );

    exerciseTimeIndex =
        std::vector<int>(
            nPaths,
            -1
        );

    exerciseFlagMatrix =
        std::vector<std::vector<bool>>(
            nPaths,
            std::vector<bool>(
                nSteps,
                false
            )
        );

    regressionDiagnostics.clear();

    std::vector<int> reversedIndices =
        exerciseIndices;

    std::reverse(
        reversedIndices.begin(),
        reversedIndices.end()
    );

    /*
        Start from final exercise date.
    */

    int lastExerciseIndex =
        reversedIndices[0];

    std::vector<double> swapRates;

    std::vector<double> immediate =
        immediateExerciseValues(
            lastExerciseIndex,
            swapRates
        );

    for(int path = 0; path < nPaths; ++path){

        cashflows[path] =
            immediate[path];

        if(immediate[path] > 0.0){

            exerciseTimeIndex[path] =
                lastExerciseIndex;

            exerciseFlagMatrix[path][lastExerciseIndex] =
                true;
        }
    }

    /*
        Move backward through exercise dates.
    */

    for(size_t idx = 1; idx < reversedIndices.size(); ++idx){

        int exerciseIndex =
            reversedIndices[idx];

        immediate =
            immediateExerciseValues(
                exerciseIndex,
                swapRates
            );

        std::vector<int> regressionPaths;

        for(int path = 0; path < nPaths; ++path){

            bool itm =
                immediate[path] > 0.0;

            bool active =
                (
                    exerciseTimeIndex[path] > exerciseIndex
                    ||
                    exerciseTimeIndex[path] == -1
                );

            if(itm && active){

                regressionPaths.push_back(
                    path
                );
            }
        }

        std::vector<double> continuation(
            nPaths,
            0.0
        );

        if(regressionPaths.size() > 5){

            std::vector<std::vector<double>> X;

            std::vector<double> y;

            for(int path : regressionPaths){

                int futureIndex =
                    exerciseTimeIndex[path];

                if(futureIndex == -1){

                    futureIndex =
                        exerciseIndices.back();
                }

                double df =
                    pathDiscountFactorBetweenIndices(
                        times,
                        ratePaths[path],
                        exerciseIndex,
                        futureIndex
                    );

                double discountedFuture =
                    cashflows[path]
                    *
                    df;

                double shortRate =
                    ratePaths[path][exerciseIndex];

                std::vector<double> basis =
                    buildBasisVector(
                        shortRate,
                        swapRates[path],
                        basisType,
                        basisDegree
                    );

                X.push_back(
                    basis
                );

                y.push_back(
                    discountedFuture
                );
            }

            std::vector<double> beta =
                solveLeastSquares(
                    X,
                    y
                );

            for(size_t k = 0; k < regressionPaths.size(); ++k){

                int path =
                    regressionPaths[k];

                double shortRate =
                    ratePaths[path][exerciseIndex];

                std::vector<double> basis =
                    buildBasisVector(
                        shortRate,
                        swapRates[path],
                        basisType,
                        basisDegree
                    );

                double fitted =
                    0.0;

                for(size_t b = 0; b < beta.size(); ++b){

                    fitted +=
                        beta[b]
                        *
                        basis[b];
                }

                continuation[path] =
                    fitted;
            }

            RegressionDiagnostic diag;

            diag.exerciseTime =
                times[exerciseIndex];

            diag.numberOfRegressionPaths =
                static_cast<int>(
                    regressionPaths.size()
                );

            diag.coefficients =
                beta;

            regressionDiagnostics.push_back(
                diag
            );
        }

        /*
            Exercise decision.
        */

        for(int path = 0; path < nPaths; ++path){

            bool itm =
                immediate[path] > 0.0;

            bool active =
                (
                    exerciseTimeIndex[path] > exerciseIndex
                    ||
                    exerciseTimeIndex[path] == -1
                );

            bool exerciseNow =
                itm
                &&
                active
                &&
                (
                    immediate[path]
                    >
                    continuation[path]
                );

            if(exerciseNow){

                cashflows[path] =
                    immediate[path];

                exerciseTimeIndex[path] =
                    exerciseIndex;

                std::fill(
                    exerciseFlagMatrix[path].begin(),
                    exerciseFlagMatrix[path].end(),
                    false
                );

                exerciseFlagMatrix[path][exerciseIndex] =
                    true;
            }
        }
    }

    /*
        Discount selected cashflows to time 0.
    */

    double sum =
        0.0;

    for(int path = 0; path < nPaths; ++path){

        int exIndex =
            exerciseTimeIndex[path];

        if(exIndex == -1){
            continue;
        }

        double df =
            pathDiscountFactorToIndex(
                times,
                ratePaths[path],
                exIndex
            );

        sum +=
            cashflows[path]
            *
            df;
    }

    return
        sum
        /
        static_cast<double>(
            nPaths
        );
}

/*
    Print exercise summary.
*/

void LSMBermudanPricer::printExerciseSummary() const {

    std::cout
        << "\nExercise Summary"
        << std::endl;

    std::cout
        << "============================================"
        << std::endl;

    for(int exIndex : exerciseIndices){

        int count =
            0;

        for(int idx : exerciseTimeIndex){

            if(idx == exIndex){
                count++;
            }
        }

        std::cout
            << "time="
            << times[exIndex]
            << ", count="
            << count
            << ", ratio="
            << static_cast<double>(count)
               /
               static_cast<double>(exerciseTimeIndex.size())
            << std::endl;
    }

    int never =
        0;

    for(int idx : exerciseTimeIndex){

        if(idx == -1){
            never++;
        }
    }

    std::cout
        << "never exercised, count="
        << never
        << ", ratio="
        << static_cast<double>(never)
           /
           static_cast<double>(exerciseTimeIndex.size())
        << std::endl;
}

/*
    Print regression diagnostics.
*/

void LSMBermudanPricer::printRegressionDiagnostics() const {

    std::cout
        << "\nRegression Diagnostics"
        << std::endl;

    std::cout
        << "============================================"
        << std::endl;

    for(const auto& diag : regressionDiagnostics){

        std::cout
            << "exercise time="
            << diag.exerciseTime
            << ", paths="
            << diag.numberOfRegressionPaths
            << ", coefficients=";

        for(double c : diag.coefficients){

            std::cout
                << c
                << " ";
        }

        std::cout
            << std::endl;
    }
}
