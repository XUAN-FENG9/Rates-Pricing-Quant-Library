#ifndef NELSON_SIEGEL_HPP_INCLUDED
#define NELSON_SIEGEL_HPP_INCLUDED
#pragma once

class NelsonSiegelCurve {

public:

    double beta0;
    double beta1;
    double beta2;
    double tau;

    NelsonSiegelCurve(
        double b0,
        double b1,
        double b2,
        double t
    );

    double zero_rate(double maturity);

    double discount_factor(double maturity);
};


#endif // NELSON_SIEGEL_HPP_INCLUDED
