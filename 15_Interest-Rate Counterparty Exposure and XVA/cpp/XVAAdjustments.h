#ifndef XVAADJUSTMENTS_H_INCLUDED
#define XVAADJUSTMENTS_H_INCLUDED


#include "ExposureMetrics.hpp"
#include "XVAData.hpp"


class CreditCurve
{
public:

    CreditCurve(
        double hazardRate,
        double recoveryRate
    );

    double hazardRate() const;

    double recoveryRate() const;

    double lossGivenDefault() const;

    double survivalProbability(
        double time
    ) const;

    Vector survivalProbabilities(
        const Vector& times
    ) const;

    Vector defaultProbabilityIncrements(
        const Vector& times
    ) const;

    void validate() const;


private:

    double hazardRate_;

    double recoveryRate_;
};


struct XVAResult
{
    double cva;

    double dva;

    double fca;

    double fba;

    double fva;

    double netValuationAdjustment;

    void printSummary() const;
};


double calculateCVA(
    const Vector& times,
    const Vector& expectedExposure,
    const Vector& discountFactors,
    const CreditCurve& counterpartyCreditCurve
);


double calculateDVA(
    const Vector& times,
    const Vector& expectedNegativeExposure,
    const Vector& discountFactors,
    const CreditCurve& bankCreditCurve
);


void calculateFundingAdjustments(
    const Vector& times,
    const Vector& expectedExposure,
    const Vector& expectedNegativeExposure,
    const Vector& discountFactors,
    double borrowingSpread,
    double lendingSpread,
    double& fca,
    double& fba,
    double& fva
);


Vector interpolateDiscountFactors(
    const Vector& tenorTimes,
    const Vector& initialDiscountFactors,
    const Vector& exposureTimes
);


XVAResult calculateXVA(
    const Vector& tenorTimes,
    const Vector& initialDiscountFactors,
    const ExposureMetricsResult& exposureMetrics,
    const CreditCurve& counterpartyCreditCurve,
    const CreditCurve& bankCreditCurve,
    double borrowingSpread,
    double lendingSpread
);

#endif // XVAADJUSTMENTS_H_INCLUDED
