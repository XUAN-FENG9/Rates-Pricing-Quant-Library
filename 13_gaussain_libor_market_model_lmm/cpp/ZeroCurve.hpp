#ifndef ZEROCURVE_HPP_INCLUDED
#define ZEROCURVE_HPP_INCLUDED


#include <vector>

/*
    ZeroCurve.hpp

    Simple continuously compounded zero curve.

    The curve provides:

        z(0,T)
        P(0,T) = exp(-z(0,T) * T)

    Linear interpolation is used between market nodes.
*/

class ZeroCurve {

private:

    std::vector<double> maturities_;
    std::vector<double> zeroRates_;

public:

    ZeroCurve(
        const std::vector<double>& maturities,
        const std::vector<double>& zeroRates
    );

    double zeroRate(
        double maturity
    ) const;

    double discountFactor(
        double maturity
    ) const;

    const std::vector<double>& maturities() const;

    const std::vector<double>& zeroRates() const;
};

#endif // ZEROCURVE_HPP_INCLUDED
