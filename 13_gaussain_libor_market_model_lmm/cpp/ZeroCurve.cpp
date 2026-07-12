#include "ZeroCurve.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>

/*
    Constructor.
*/

ZeroCurve::ZeroCurve(
    const std::vector<double>& maturities,
    const std::vector<double>& zeroRates
)
    :
    maturities_(maturities),
    zeroRates_(zeroRates)
{

    if(maturities_.size() != zeroRates_.size()){

        throw std::invalid_argument(
            "Maturity and zero-rate vectors must have equal length."
        );
    }

    if(maturities_.size() < 2){

        throw std::invalid_argument(
            "At least two curve points are required."
        );
    }

    for(std::size_t i = 1; i < maturities_.size(); ++i){

        if(maturities_[i] <= maturities_[i - 1]){

            throw std::invalid_argument(
                "Curve maturities must be strictly increasing."
            );
        }
    }
}

/*
    Linear interpolation of continuously compounded zero rates.
*/

double ZeroCurve::zeroRate(
    double maturity
) const {

    if(maturity <= maturities_.front()){

        return zeroRates_.front();
    }

    if(maturity >= maturities_.back()){

        return zeroRates_.back();
    }

    auto upper =
        std::upper_bound(
            maturities_.begin(),
            maturities_.end(),
            maturity
        );

    std::size_t upperIndex =
        static_cast<std::size_t>(
            upper - maturities_.begin()
        );

    std::size_t lowerIndex =
        upperIndex - 1;

    double t0 =
        maturities_[lowerIndex];

    double t1 =
        maturities_[upperIndex];

    double r0 =
        zeroRates_[lowerIndex];

    double r1 =
        zeroRates_[upperIndex];

    double weight =
        (maturity - t0)
        /
        (t1 - t0);

    return
        r0
        +
        weight
        *
        (r1 - r0);
}

/*
    Continuously compounded discount factor.
*/

double ZeroCurve::discountFactor(
    double maturity
) const {

    if(maturity <= 0.0){

        return 1.0;
    }

    return std::exp(
        -zeroRate(maturity)
        *
        maturity
    );
}

const std::vector<double>& ZeroCurve::maturities() const {

    return maturities_;
}

const std::vector<double>& ZeroCurve::zeroRates() const {

    return zeroRates_;
}
