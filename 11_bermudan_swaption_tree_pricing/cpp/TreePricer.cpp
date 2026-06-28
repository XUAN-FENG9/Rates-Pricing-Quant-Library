#include "TreePricer.hpp"

#include <cmath>
#include <algorithm>

/*
    Constructor.
*/

BermudanSwaptionTreePricer::BermudanSwaptionTreePricer(
    HullWhiteBinomialTree* tree_,
    BermudanSwaption* instrument_
){

    tree = tree_;
    instrument = instrument_;
}

/*
    Check whether t is an exercise date.
*/

bool BermudanSwaptionTreePricer::isExerciseTime(
    double t,
    double tolerance
) const {

    for(double exerciseTime : instrument->exerciseDates){

        if(std::abs(exerciseTime - t) < tolerance){

            return true;
        }
    }

    return false;
}

/*
    Price by backward induction.

    At each node:

        continuation value
        exercise value
        option value = max(exercise, continuation)
        exercise flag
*/

double BermudanSwaptionTreePricer::price(){

    int nSteps =
        tree->nSteps;

    valueTree.clear();
    exerciseValueTree.clear();
    continuationValueTree.clear();
    exerciseFlagTree.clear();

    for(int step = 0; step <= nSteps; ++step){

        valueTree.push_back(
            std::vector<double>(
                step + 1,
                0.0
            )
        );

        exerciseValueTree.push_back(
            std::vector<double>(
                step + 1,
                0.0
            )
        );

        continuationValueTree.push_back(
            std::vector<double>(
                step + 1,
                0.0
            )
        );

        exerciseFlagTree.push_back(
            std::vector<bool>(
                step + 1,
                false
            )
        );
    }

    /*
        Terminal step.
    */

    double terminalTime =
        tree->times[nSteps];

    for(int node = 0; node <= nSteps; ++node){

        double r =
            tree->rates[nSteps][node];

        if(isExerciseTime(terminalTime)){

            double ex =
                instrument->exerciseValue(
                    *(tree->model),
                    terminalTime,
                    r
                );

            exerciseValueTree[nSteps][node] =
                ex;

            valueTree[nSteps][node] =
                ex;

            exerciseFlagTree[nSteps][node] =
                ex > 0.0;
        }
    }

    /*
        Backward induction.
    */

    for(int step = nSteps - 1; step >= 0; --step){

        double t =
            tree->times[step];

        for(int node = 0; node <= step; ++node){

            double pUp =
                tree->probabilities[step][node];

            double pDown =
                1.0 - pUp;

            double df =
                tree->discountFactorOneStep(
                    step,
                    node
                );

            double continuation =
                df
                *
                (
                    pDown
                    *
                    valueTree[step + 1][node]
                    +
                    pUp
                    *
                    valueTree[step + 1][node + 1]
                );

            continuationValueTree[step][node] =
                continuation;

            double nodeValue =
                continuation;

            if(isExerciseTime(t)){

                double r =
                    tree->rates[step][node];

                double exercise =
                    instrument->exerciseValue(
                        *(tree->model),
                        t,
                        r
                    );

                exerciseValueTree[step][node] =
                    exercise;

                if(exercise > continuation){

                    nodeValue =
                        exercise;

                    exerciseFlagTree[step][node] =
                        true;
                }
            }

            valueTree[step][node] =
                nodeValue;
        }
    }

    return
        valueTree[0][0];
}
