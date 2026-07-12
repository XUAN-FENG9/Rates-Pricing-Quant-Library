#ifndef REGRESSIONBASIS_HPP_INCLUDED
#define REGRESSIONBASIS_HPP_INCLUDED

#include <string>
#include <vector>

/*
    RegressionBasis.hpp

    Basis functions for Longstaff-Schwartz regression.
*/

std::vector<double> polynomialBasis(
    double x,
    int degree
);

std::vector<double> rateAndSwapBasis(
    double shortRate,
    double swapRate,
    int degree
);

std::vector<double> buildBasisVector(
    double shortRate,
    double swapRate,
    const std::string& basisType,
    int degree
);

#endif // REGRESSIONBASIS_HPP_INCLUDED
