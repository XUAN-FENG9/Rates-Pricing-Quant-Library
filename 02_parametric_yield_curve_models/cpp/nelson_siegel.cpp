#include "nelson_siegel.hpp"
#include <cmath>

NelsonSiegelCurve::NelsonSiegelCurve(
    double b0,
    double b1,
    double b2,
    double t
){

    beta0 = b0;
    beta1 = b1;
    beta2 = b2;
    tau = t;
}

double NelsonSiegelCurve::zero_rate(
    double maturity
){

    double x = maturity / tau;

    double factor1 =
        (1.0 - exp(-x)) / x;

    double factor2 =
        factor1 - exp(-x);

    return
        beta0
        + beta1 * factor1
        + beta2 * factor2;
}

double NelsonSiegelCurve::discount_factor(
    double maturity
){

    double r = zero_rate(maturity);

    return exp(-r * maturity);
}
