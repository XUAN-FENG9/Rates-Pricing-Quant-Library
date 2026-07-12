#include "RegressionBasis.hpp"

#include <cmath>
#include <string>
#include <stdexcept>

/*
    Polynomial basis:

        1, x, x^2, ..., x^degree
*/

std::vector<double> polynomialBasis(
    double x,
    int degree
){

    std::vector<double> basis;

    basis.push_back(1.0);

    for(int d = 1; d <= degree; ++d){

        basis.push_back(
            std::pow(
                x,
                d
            )
        );
    }

    return basis;
}

/*
    Basis using both short rate and swap rate.

    degree = 2:

        1, r, s, r*s, r^2, s^2
*/

std::vector<double> rateAndSwapBasis(
    double shortRate,
    double swapRate,
    int degree
){

    std::vector<double> basis;

    basis.push_back(1.0);
    basis.push_back(shortRate);
    basis.push_back(swapRate);
    basis.push_back(shortRate * swapRate);

    if(degree >= 2){

        basis.push_back(shortRate * shortRate);
        basis.push_back(swapRate * swapRate);
    }

    if(degree >= 3){

        basis.push_back(shortRate * shortRate * shortRate);
        basis.push_back(swapRate * swapRate * swapRate);
        basis.push_back(shortRate * shortRate * swapRate);
        basis.push_back(shortRate * swapRate * swapRate);
    }

    return basis;
}

/*
    Build basis vector by basis type.
*/

std::vector<double> buildBasisVector(
    double shortRate,
    double swapRate,
    const std::string& basisType,
    int degree
){

    if(basisType == "rate"){

        return polynomialBasis(
            shortRate,
            degree
        );

    } else if(basisType == "swap"){

        return polynomialBasis(
            swapRate,
            degree
        );

    } else if(basisType == "rate_swap"){

        return rateAndSwapBasis(
            shortRate,
            swapRate,
            degree
        );

    } else {

        throw std::runtime_error(
            "basisType must be rate, swap, or rate_swap."
        );
    }
}
