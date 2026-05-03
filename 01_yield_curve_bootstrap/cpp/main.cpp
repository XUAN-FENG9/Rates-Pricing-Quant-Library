#include <iostream>
#include "curve.h"

int main(){

    YieldCurve curve;

    curve.add(1,0.98);
    curve.add(2,0.95);

    std::cout << curve.forward(1,2) << std::endl;

    return 0;
}
