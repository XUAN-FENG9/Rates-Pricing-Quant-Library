#include "HullWhiteTree.hpp"

#include <cmath>
#include <algorithm>

/*
    Constructor.
*/

HullWhiteBinomialTree::HullWhiteBinomialTree(
    HullWhiteModel* model_,
    double maturity_,
    int nSteps_,
    double r0_
){

    model = model_;
    maturity = maturity_;
    nSteps = nSteps_;
    r0 = r0_;

    dt =
        maturity
        /
        static_cast<double>(
            nSteps
        );

    deltaR =
        model->sigma
        *
        std::sqrt(
            dt
        );

    times.resize(
        nSteps + 1
    );

    for(int i = 0; i <= nSteps; ++i){

        times[i] =
            i
            *
            dt;
    }

    buildTree();
}

/*
    Node rate:

        r(i,j) = r0 + (2j - i) deltaR
*/

double HullWhiteBinomialTree::nodeRate(
    int step,
    int node
) const {

    return
        r0
        +
        (
            2.0
            *
            node
            -
            step
        )
        *
        deltaR;
}

/*
    Transition probability.

    Drift:

        mu(t,r) = theta(t) - a r

    Match:

        E[Delta r] = (2p - 1) deltaR = mu dt

    Therefore:

        p = 0.5 + mu dt / (2 deltaR)
*/

double HullWhiteBinomialTree::transitionProbability(
    int step,
    int node
) const {

    double t =
        times[step];

    double r =
        nodeRate(
            step,
            node
        );

    double drift =
        model->shortRateDrift(
            t,
            r
        );

    if(std::abs(deltaR) < 1e-12){
        return 0.5;
    }

    double p =
        0.5
        +
        drift
        *
        dt
        /
        (
            2.0
            *
            deltaR
        );

    return std::min(
        0.99,
        std::max(
            0.01,
            p
        )
    );
}

/*
    Build rate and probability trees.
*/

void HullWhiteBinomialTree::buildTree(){

    rates.clear();
    probabilities.clear();

    for(int step = 0; step <= nSteps; ++step){

        std::vector<double> stepRates;

        for(int node = 0; node <= step; ++node){

            stepRates.push_back(
                nodeRate(
                    step,
                    node
                )
            );
        }

        rates.push_back(
            stepRates
        );
    }

    for(int step = 0; step < nSteps; ++step){

        std::vector<double> stepProbs;

        for(int node = 0; node <= step; ++node){

            stepProbs.push_back(
                transitionProbability(
                    step,
                    node
                )
            );
        }

        probabilities.push_back(
            stepProbs
        );
    }
}

/*
    One-step discount factor:

        exp(-r dt)
*/

double HullWhiteBinomialTree::discountFactorOneStep(
    int step,
    int node
) const {

    double r =
        rates[step][node];

    return
        std::exp(
            -r
            *
            dt
        );
}
