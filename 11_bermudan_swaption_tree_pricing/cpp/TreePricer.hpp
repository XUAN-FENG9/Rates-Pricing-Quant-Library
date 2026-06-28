#ifndef TREEPRICER_HPP_INCLUDED
#define TREEPRICER_HPP_INCLUDED

#include <vector>

#include "HullWhiteTree.hpp"
#include "BermudanSwaption.hpp"

/*
    TreePricer.hpp

    Bermudan swaption pricing by backward induction.

    This version stores four trees:

    - valueTree
    - exerciseValueTree
    - continuationValueTree
    - exerciseFlagTree
*/

class BermudanSwaptionTreePricer {

public:

    HullWhiteBinomialTree* tree;

    BermudanSwaption* instrument;

    std::vector<std::vector<double>> valueTree;

    std::vector<std::vector<double>> exerciseValueTree;

    std::vector<std::vector<double>> continuationValueTree;

    std::vector<std::vector<bool>> exerciseFlagTree;

    BermudanSwaptionTreePricer(
        HullWhiteBinomialTree* tree_,
        BermudanSwaption* instrument_
    );

    bool isExerciseTime(
        double t,
        double tolerance = 1e-8
    ) const;

    double price();
};

#endif // TREEPRICER_HPP_INCLUDED
