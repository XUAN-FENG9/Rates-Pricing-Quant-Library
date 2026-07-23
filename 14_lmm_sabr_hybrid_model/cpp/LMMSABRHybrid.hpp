#ifndef LMMSABRHYBRID_HPP_INCLUDED
#define LMMSABRHYBRID_HPP_INCLUDED


#include <cstddef>

#include "Matrix.hpp"
#include "SABRParameters.hpp"


class LMMSABRHybrid
{
public:

    LMMSABRHybrid(
        const Vector& resetTimes,
        const Vector& accruals,
        const Vector& initialForwards,
        const Vector& initialDiscountFactors,
        const Matrix& correlationLoadings,
        const SABRParameters& sabrParameters,
        double volatilityLevel,
        double volatilityDecay,
        double volatilityFloor
    );

    std::size_t numberOfForwards() const;
    std::size_t numberOfFactors() const;

    const Vector& resetTimes() const;
    const Vector& accruals() const;
    const Vector& initialForwards() const;
    const Vector& initialDiscountFactors() const;

    const SABRParameters& sabrParameters() const;

    Vector activeMask(
        double time
    ) const;

    Vector deterministicVolatilities(
        double time
    ) const;

    Matrix factorLoadings(
        double time,
        const Vector& forwards,
        const Vector& alpha
    ) const;

    Matrix instantaneousCovarianceMatrix(
        double time,
        const Vector& forwards,
        const Vector& alpha
    ) const;

    Vector terminalMeasureDrift(
        double time,
        const Vector& forwards,
        const Vector& alpha
    ) const;

    Vector effectiveForwardShocks(
        double time,
        const Vector& forwards,
        const Vector& alpha,
        const Vector& rateFactorShocks
    ) const;

    void evolve(
        double time,
        const Vector& forwards,
        const Vector& alpha,
        double dt,
        const Vector& rateFactorShocks,
        const Vector& independentVolatilityShocks,
        Vector& nextForwards,
        Vector& nextAlpha
    ) const;

    Vector discountFactorsFromForwards(
        const Vector& forwards,
        std::size_t startIndex
    ) const;

    double terminalBondFromForwards(
        const Vector& forwards,
        std::size_t startIndex
    ) const;

    double initialTerminalBond() const;

    void validateState(
        const Vector& forwards,
        const Vector& alpha
    ) const;

    void printSummary() const;


private:

    Vector resetTimes_;
    Vector accruals_;
    Vector initialForwards_;
    Vector initialDiscountFactors_;

    Matrix correlationLoadings_;

    SABRParameters sabrParameters_;

    double volatilityLevel_;
    double volatilityDecay_;
    double volatilityFloor_;

    std::size_t numberOfForwards_;
    std::size_t numberOfFactors_;

    static double dotProduct(
        const Vector& first,
        const Vector& second
    );

    static double vectorNorm(
        const Vector& values
    );

    void validateModelInputs() const;
};

#endif // LMMSABRHYBRID_HPP_INCLUDED
