#ifndef HULLWHITETREE_HPP_INCLUDED
#define HULLWHITETREE_HPP_INCLUDED

#include <vector>

#include "HullWhiteModel.hpp"

/*
    HullWhiteTree.hpp

    Educational recombining binomial approximation to Hull-White.

    Node rate:

        r(i,j) = r0 + (2j - i) deltaR

    where:
        i = time step
        j = node index

    deltaR is node spacing:

        deltaR = sigma * sqrt(dt)

    Drift is incorporated through transition probabilities.
*/

class HullWhiteBinomialTree {

public:

    HullWhiteModel* model;

    double maturity;
    int nSteps;

    double dt;
    double r0;
    double deltaR;

    std::vector<double> times;

    std::vector<std::vector<double>> rates;

    std::vector<std::vector<double>> probabilities;

    HullWhiteBinomialTree(
        HullWhiteModel* model_,
        double maturity_,
        int nSteps_,
        double r0_
    );

    double nodeRate(
        int step,
        int node
    ) const;

    double transitionProbability(
        int step,
        int node
    ) const;

    void buildTree();

    double discountFactorOneStep(
        int step,
        int node
    ) const;
};

#endif // HULLWHITETREE_HPP_INCLUDED
