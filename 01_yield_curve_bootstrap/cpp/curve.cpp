#include "curve.h"
#include <cmath>

void YieldCurve::add(double T, double DF){
    t.push_back(T);
    df.push_back(DF);
}

double YieldCurve::get_df(double T){
    for(size_t i=1;i<t.size();++i){
        if(T<t[i]){
            double w=(T-t[i-1])/(t[i]-t[i-1]);
            return exp((1-w)*log(df[i-1]) + w*log(df[i]));
        }
    }
    return df.back();
}

double YieldCurve::forward(double t1,double t2){
    double df1=get_df(t1);
    double df2=get_df(t2);
    return (df1/df2 -1)/(t2-t1);
}
