#ifndef SABRMODEL_HPP_INCLUDED
#define SABRMODEL_HPP_INCLUDED

#include <vector>

class SABRModel {

public:
    double alpha;
    double beta;
    double rho;
    double nu;

    SABRModel(
        double alpha_,
        double beta_,
        double rho_,
        double nu_
    );

    double blackVol(
        double forward,
        double strike,
        double expiry
    ) const;

    std::vector<double> blackVolVector(
        double forward,
        const std::vector<double>& strikes,
        double expiry
    ) const;
};

#endif // SABRMODEL_HPP_INCLUDED
