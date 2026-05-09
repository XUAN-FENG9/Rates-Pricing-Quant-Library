#include <iostream>
#include "nelson_siegel.hpp"

int main(){

    NelsonSiegelCurve curve(
        0.03,
        -0.02,
        0.02,
        2.0
    );

    for(double t : {1,2,5,10,30}){

        std::cout
            << "T=" << t
            << " Rate="
            << curve.zero_rate(t)
            << std::endl;
    }

    return 0;
}
