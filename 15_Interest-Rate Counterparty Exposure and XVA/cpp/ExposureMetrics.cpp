#include "ExposureMetrics.hpp"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>


namespace
{
    double quantile(
        Vector values,
        double confidenceLevel
    )
    {
        if (values.empty())
        {
            throw std::invalid_argument(
                "Cannot calculate a quantile "
                "from an empty vector."
            );
        }

        std::sort(
            values.begin(),
            values.end()
        );

        if (values.size() == 1)
        {
            return values.front();
        }

        double position =
            confidenceLevel
            *
            static_cast<double>(
                values.size() - 1
            );

        std::size_t lowerIndex =
            static_cast<std::size_t>(
                std::floor(
                    position
                )
            );

        std::size_t upperIndex =
            static_cast<std::size_t>(
                std::ceil(
                    position
                )
            );

        double weight =
            position
            -
            static_cast<double>(
                lowerIndex
            );

        return
            values[lowerIndex]
            *
            (1.0 - weight)
            +
            values[upperIndex]
            *
            weight;
    }
}


double ExposureMetricsResult::maximumEE() const
{
    return *std::max_element(
        expectedExposure.begin(),
        expectedExposure.end()
    );
}


double ExposureMetricsResult::maximumENE() const
{
    return *std::max_element(
        expectedNegativeExposure.begin(),
        expectedNegativeExposure.end()
    );
}


double ExposureMetricsResult::maximumPFE() const
{
    return *std::max_element(
        potentialFutureExposure.begin(),
        potentialFutureExposure.end()
    );
}


void ExposureMetricsResult::printSummary() const
{
    std::cout
        << "Exposure Summary\n"
        << "------------------------------\n"
        << "EPE: "
        << expectedPositiveExposure
        << "\n"
        << "Average ENE: "
        << averageExpectedNegativeExposure
        << "\n"
        << "Maximum EE: "
        << maximumEE()
        << "\n"
        << "Maximum ENE: "
        << maximumENE()
        << "\n"
        << "Maximum PFE: "
        << maximumPFE()
        << "\n"
        << "PFE confidence: "
        << pfeConfidenceLevel
        << "\n";
}


void ExposureMetricsResult::printProfile() const
{
    std::cout
        << "\n"
        << "Exposure Profile\n"
        << "--------------------------------------------------\n"
        << "Time"
        << "\tEE"
        << "\tENE"
        << "\tPFE\n";

    for (std::size_t index = 0;
         index < times.size();
         ++index)
    {
        std::cout
            << times[index]
            << "\t"
            << expectedExposure[index]
            << "\t"
            << expectedNegativeExposure[index]
            << "\t"
            << potentialFutureExposure[index]
            << "\n";
    }
}


Matrix positiveExposure(
    const Matrix& portfolioValues
)
{
    Matrix result =
        portfolioValues;

    for (Vector& path :
         result)
    {
        for (double& value :
             path)
        {
            value = std::max(
                value,
                0.0
            );
        }
    }

    return result;
}


Matrix negativeExposure(
    const Matrix& portfolioValues
)
{
    Matrix result =
        portfolioValues;

    for (Vector& path :
         result)
    {
        for (double& value :
             path)
        {
            value = std::max(
                -value,
                0.0
            );
        }
    }

    return result;
}


Vector meanAcrossPaths(
    const Matrix& values
)
{
    if (values.empty())
    {
        return Vector();
    }

    std::size_t numberOfPaths =
        values.size();

    std::size_t numberOfTimes =
        values.front().size();

    Vector means(
        numberOfTimes,
        0.0
    );

    for (const Vector& path :
         values)
    {
        if (path.size() !=
            numberOfTimes)
        {
            throw std::invalid_argument(
                "All paths must have equal length."
            );
        }

        for (std::size_t timeIndex = 0;
             timeIndex <
                 numberOfTimes;
             ++timeIndex)
        {
            means[timeIndex] +=
                path[timeIndex];
        }
    }

    for (double& value :
         means)
    {
        value /=
            static_cast<double>(
                numberOfPaths
            );
    }

    return means;
}


Vector potentialFutureExposure(
    const Matrix& portfolioValues,
    double confidenceLevel
)
{
    if (confidenceLevel <= 0.0 ||
        confidenceLevel >= 1.0)
    {
        throw std::invalid_argument(
            "confidenceLevel must lie between zero and one."
        );
    }

    Matrix positive =
        positiveExposure(
            portfolioValues
        );

    if (positive.empty())
    {
        return Vector();
    }

    std::size_t numberOfTimes =
        positive.front().size();

    Vector pfe(
        numberOfTimes,
        0.0
    );

    for (std::size_t timeIndex = 0;
         timeIndex <
             numberOfTimes;
         ++timeIndex)
    {
        Vector valuesAtTime;

        valuesAtTime.reserve(
            positive.size()
        );

        for (const Vector& path :
             positive)
        {
            valuesAtTime.push_back(
                path[timeIndex]
            );
        }

        pfe[timeIndex] =
            quantile(
                valuesAtTime,
                confidenceLevel
            );
    }

    return pfe;
}


double timeWeightedAverage(
    const Vector& times,
    const Vector& values
)
{
    if (times.size() !=
        values.size())
    {
        throw std::invalid_argument(
            "times and values must have equal size."
        );
    }

    if (times.empty())
    {
        return 0.0;
    }

    if (times.size() == 1)
    {
        return values.front();
    }

    double horizon =
        times.back()
        -
        times.front();

    if (horizon <= 0.0)
    {
        double total =
            std::accumulate(
                values.begin(),
                values.end(),
                0.0
            );

        return
            total
            /
            static_cast<double>(
                values.size()
            );
    }

    double integral =
        0.0;

    for (std::size_t index = 0;
         index + 1 <
             times.size();
         ++index)
    {
        double dt =
            times[index + 1]
            -
            times[index];

        integral +=
            0.5
            *
            (
                values[index]
                +
                values[index + 1]
            )
            *
            dt;
    }

    return
        integral
        /
        horizon;
}


ExposureMetricsResult calculateExposureMetrics(
    const Vector& times,
    const Matrix& portfolioValues,
    double pfeConfidenceLevel
)
{
    if (portfolioValues.empty())
    {
        throw std::invalid_argument(
            "portfolioValues cannot be empty."
        );
    }

    if (portfolioValues.front().size() !=
        times.size())
    {
        throw std::invalid_argument(
            "Portfolio time dimension does not "
            "match the exposure times."
        );
    }

    ExposureMetricsResult result;

    result.times =
        times;

    result.positiveExposure =
        positiveExposure(
            portfolioValues
        );

    result.negativeExposure =
        negativeExposure(
            portfolioValues
        );

    result.expectedExposure =
        meanAcrossPaths(
            result.positiveExposure
        );

    result.expectedNegativeExposure =
        meanAcrossPaths(
            result.negativeExposure
        );

    result.potentialFutureExposure =
        potentialFutureExposure(
            portfolioValues,
            pfeConfidenceLevel
        );

    result.pfeConfidenceLevel =
        pfeConfidenceLevel;

    result.expectedPositiveExposure =
        timeWeightedAverage(
            times,
            result.expectedExposure
        );

    result.averageExpectedNegativeExposure =
        timeWeightedAverage(
            times,
            result.expectedNegativeExposure
        );

    return result;
}
