#include "SABRParameters.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>


Vector SABRParameters::expandParameter(
    std::size_t numberOfForwards,
    double value
)
{
    return Vector(
        numberOfForwards,
        value
    );
}


void SABRParameters::validateVectorSize(
    const Vector& values,
    std::size_t expectedSize,
    const std::string& parameterName
)
{
    if (values.size() != expectedSize)
    {
        throw std::invalid_argument(
            parameterName +
            " must contain one value per forward rate."
        );
    }
}


SABRParameters::SABRParameters(
    std::size_t numberOfForwards,
    double alpha0,
    double beta,
    double rho,
    double nu,
    double shift,
    double alphaFloor,
    double alphaCap
)
    :
    numberOfForwards_(numberOfForwards),
    alpha0_(
        expandParameter(
            numberOfForwards,
            alpha0
        )
    ),
    beta_(
        expandParameter(
            numberOfForwards,
            beta
        )
    ),
    rho_(
        expandParameter(
            numberOfForwards,
            rho
        )
    ),
    nu_(
        expandParameter(
            numberOfForwards,
            nu
        )
    ),
    shift_(
        expandParameter(
            numberOfForwards,
            shift
        )
    ),
    alphaFloor_(alphaFloor),
    alphaCap_(alphaCap)
{
    validate();
}


SABRParameters::SABRParameters(
    const Vector& alpha0,
    const Vector& beta,
    const Vector& rho,
    const Vector& nu,
    const Vector& shift,
    double alphaFloor,
    double alphaCap
)
    :
    numberOfForwards_(alpha0.size()),
    alpha0_(alpha0),
    beta_(beta),
    rho_(rho),
    nu_(nu),
    shift_(shift),
    alphaFloor_(alphaFloor),
    alphaCap_(alphaCap)
{
    validateVectorSize(
        beta_,
        numberOfForwards_,
        "beta"
    );

    validateVectorSize(
        rho_,
        numberOfForwards_,
        "rho"
    );

    validateVectorSize(
        nu_,
        numberOfForwards_,
        "nu"
    );

    validateVectorSize(
        shift_,
        numberOfForwards_,
        "shift"
    );

    validate();
}


std::size_t SABRParameters::numberOfForwards() const
{
    return numberOfForwards_;
}


const Vector& SABRParameters::alpha0() const
{
    return alpha0_;
}


const Vector& SABRParameters::beta() const
{
    return beta_;
}


const Vector& SABRParameters::rho() const
{
    return rho_;
}


const Vector& SABRParameters::nu() const
{
    return nu_;
}


const Vector& SABRParameters::shift() const
{
    return shift_;
}


double SABRParameters::alphaFloor() const
{
    return alphaFloor_;
}


double SABRParameters::alphaCap() const
{
    return alphaCap_;
}


void SABRParameters::validate() const
{
    if (numberOfForwards_ == 0)
    {
        throw std::invalid_argument(
            "The number of forward rates must be positive."
        );
    }

    if (alphaFloor_ <= 0.0)
    {
        throw std::invalid_argument(
            "alphaFloor must be strictly positive."
        );
    }

    if (alphaCap_ <= alphaFloor_)
    {
        throw std::invalid_argument(
            "alphaCap must exceed alphaFloor."
        );
    }

    for (std::size_t i = 0;
         i < numberOfForwards_;
         ++i)
    {
        if (!std::isfinite(alpha0_[i]) ||
            !std::isfinite(beta_[i]) ||
            !std::isfinite(rho_[i]) ||
            !std::isfinite(nu_[i]) ||
            !std::isfinite(shift_[i]))
        {
            throw std::invalid_argument(
                "All SABR parameters must be finite."
            );
        }

        if (alpha0_[i] <= 0.0)
        {
            throw std::invalid_argument(
                "alpha0 must be strictly positive."
            );
        }

        if (beta_[i] < 0.0 ||
            beta_[i] > 1.0)
        {
            throw std::invalid_argument(
                "beta must lie between zero and one."
            );
        }

        if (rho_[i] <= -1.0 ||
            rho_[i] >= 1.0)
        {
            throw std::invalid_argument(
                "rho must lie strictly between -1 and 1."
            );
        }

        if (nu_[i] < 0.0)
        {
            throw std::invalid_argument(
                "nu must be non-negative."
            );
        }

        if (shift_[i] < 0.0)
        {
            throw std::invalid_argument(
                "shift must be non-negative."
            );
        }
    }
}


void SABRParameters::printSummary() const
{
    std::cout
        << "SABR Parameters\n"
        << "------------------------------\n"
        << "Number of forwards: "
        << numberOfForwards_
        << "\n"
        << "Alpha floor: "
        << alphaFloor_
        << "\n"
        << "Alpha cap: "
        << alphaCap_
        << "\n";

    std::size_t numberToPrint =
        std::min<std::size_t>(
            numberOfForwards_,
            10
        );

    std::cout
        << "\n"
        << "Index"
        << "\tAlpha0"
        << "\tBeta"
        << "\tRho"
        << "\tNu"
        << "\tShift\n";

    for (std::size_t i = 0;
         i < numberToPrint;
         ++i)
    {
        std::cout
            << i
            << "\t"
            << alpha0_[i]
            << "\t"
            << beta_[i]
            << "\t"
            << rho_[i]
            << "\t"
            << nu_[i]
            << "\t"
            << shift_[i]
            << "\n";
    }
}
