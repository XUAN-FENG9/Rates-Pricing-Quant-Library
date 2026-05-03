#pragma once
#include <vector>

class YieldCurve {
public:
    std::vector<double> t;
    std::vector<double> df;

    void add(double T, double DF);
    double get_df(double T);
    double forward(double t1, double t2);
};
