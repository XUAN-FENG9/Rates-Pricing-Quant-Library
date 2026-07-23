#ifndef SABRPARAMETERS_HPP_INCLUDED
#define SABRPARAMETERS_HPP_INCLUDED


#include <cstddef>
#include <string>

#include "Matrix.hpp"


class SABRParameters
{
public:

    SABRParameters(
        std::size_t numberOfForwards,
        double alpha0,
        double beta,
        double rho,
        double nu,
        double shift,
        double alphaFloor = 1.0e-8,
        double alphaCap = 10.0
    );

    SABRParameters(
        const Vector& alpha0,
        const Vector& beta,
        const Vector& rho,
        const Vector& nu,
        const Vector& shift,
        double alphaFloor = 1.0e-8,
        double alphaCap = 10.0
    );

    std::size_t numberOfForwards() const;

    const Vector& alpha0() const;
    const Vector& beta() const;
    const Vector& rho() const;
    const Vector& nu() const;
    const Vector& shift() const;

    double alphaFloor() const;
    double alphaCap() const;

    void validate() const;

    void printSummary() const;


private:

    std::size_t numberOfForwards_;

    Vector alpha0_;
    Vector beta_;
    Vector rho_;
    Vector nu_;
    Vector shift_;

    double alphaFloor_;
    double alphaCap_;

    static Vector expandParameter(
        std::size_t numberOfForwards,
        double value
    );

    static void validateVectorSize(
        const Vector& values,
        std::size_t expectedSize,
        const std::string& parameterName
    );
};

#endif // SABRPARAMETERS_HPP_INCLUDED
