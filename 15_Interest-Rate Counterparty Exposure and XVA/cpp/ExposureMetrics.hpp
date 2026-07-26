#ifndef EXPOSUREMETRICS_H_INCLUDED
#define EXPOSUREMETRICS_H_INCLUDED

#include <cstddef>

#include "XVAData.hpp"


struct ExposureMetricsResult
{
    Vector times;

    Matrix positiveExposure;

    Matrix negativeExposure;

    Vector expectedExposure;

    Vector expectedNegativeExposure;

    Vector potentialFutureExposure;

    double pfeConfidenceLevel;

    double expectedPositiveExposure;

    double averageExpectedNegativeExposure;

    double maximumEE() const;

    double maximumENE() const;

    double maximumPFE() const;

    void printSummary() const;

    void printProfile() const;
};


Matrix positiveExposure(
    const Matrix& portfolioValues
);


Matrix negativeExposure(
    const Matrix& portfolioValues
);


Vector meanAcrossPaths(
    const Matrix& values
);


Vector potentialFutureExposure(
    const Matrix& portfolioValues,
    double confidenceLevel
);


double timeWeightedAverage(
    const Vector& times,
    const Vector& values
);


ExposureMetricsResult calculateExposureMetrics(
    const Vector& times,
    const Matrix& portfolioValues,
    double pfeConfidenceLevel = 0.95
);

#endif // EXPOSUREMETRICS_H_INCLUDED
