#include "curve.h"

double price_swap(YieldCurve& ois, YieldCurve& libor, int maturity, double K){

    double fixed=0, floating=0;

    for(int i=1;i<=maturity;i++){
        double df = ois.get_df(i);

        fixed += K * df;

        double fwd = libor.forward(i-1,i);

        floating += fwd * df;
    }

    return floating - fixed;
}
