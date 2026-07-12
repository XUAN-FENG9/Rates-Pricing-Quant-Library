/*
† In memory of my beloved grandfather - Heshun Feng (1942-2026), who passed away today (11th July 2026). His love and encouragement will forever inspire me.
*/

#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#include "Correlation.hpp"
#include "Diagnostics.hpp"
#include "GaussianLMM.hpp"
#include "GaussianLMMVolatility.hpp"
#include "LMMPricing.hpp"
#include "LMMSimulation.hpp"
#include "TenorStructure.hpp"
#include "ZeroCurve.hpp"

int main(){

    try {

        std::cout
            << std::fixed
            << std::setprecision(8);

        /*
            1. Initial zero curve.
        */

        std::vector<double> maturities = {
            0.0,
            0.5,
            1.0,
            2.0,
            3.0,
            5.0,
            7.0,
            10.0
        };

        std::vector<double> zeroRates = {
            0.0200,
            0.0210,
            0.0220,
            0.0240,
            0.0250,
            0.0270,
            0.0285,
            0.0300
        };

        ZeroCurve curve(
            maturities,
            zeroRates
        );

        /*
            2. Semiannual tenor from 0Y to 10Y.
        */

        TenorStructure tenor(
            0.0,
            10.0,
            2
        );

        std::vector<double> initialForwards =
            tenor.initialForwardRates(
                curve
            );

        std::vector<double> initialDiscountFactors =
            tenor.initialDiscountFactors(
                curve
            );

        /*
            3. Exponential correlation.
        */

        std::vector<double> resetTimes(
            tenor.times().begin(),
            tenor.times().end() - 1
        );

        Matrix correlationMatrix =
            exponentialCorrelationMatrix(
                resetTimes,
                0.10
            );

        /*
            4. PCA reduction to three factors.
        */

        Matrix correlationLoadings =
            principalComponentLoadings(
                correlationMatrix,
                3
            );

        /*
            5. Gaussian normal-volatility model.
        */

        GaussianLMMVolatility volatilityModel(
            resetTimes,
            0.01,
            0.05,
            0.001
        );

        /*
            6. Build terminal-measure Gaussian LMM.
        */

        GaussianLMM model(
            tenor,
            initialForwards,
            volatilityModel,
            correlationLoadings,
            initialDiscountFactors
        );

        printForwardCurve(
            model
        );

        printCorrelationSummary(
            correlationMatrix
        );

        /*
            7. Inspect terminal-measure drift.
        */

        std::vector<double> initialDrift =
            model.terminalMeasureDrift(
                0.0,
                initialForwards
            );

        std::cout
            << "\nTerminal-Measure Drift"
            << std::endl;

        std::cout
            << "============================================================"
            << std::endl;

        for(int i = 0; i < model.numberOfForwards(); ++i){

            std::cout
                << "L["
                << i
                << "] drift = "
                << initialDrift[i]
                << std::endl;
        }

        std::cout
            << "\nLast-forward drift should be zero: "
            << initialDrift.back()
            << std::endl;

        /*
            8. Monte Carlo simulation.
        */

        LMMSimulationResult simulation =
            simulateGaussianLMM(
                model,
                5.0,
                100,
                5000,
                42,
                true
            );

        printSimulationSummary(
            model,
            simulation
        );

        /*
            9. Caplet pricing.

            Reset:
                2Y

            Payment:
                2.5Y
        */

        double capletPrice =
            priceCapletMonteCarlo(
                model,
                simulation,
                2.0,
                0.045,
                1000000.0
            );

        /*
            10. European payer swaption.

            Expiry:
                2Y

            Underlying swap:
                2Y to 7Y
        */

        double swaptionPrice =
            pricePayerSwaptionMonteCarlo(
                model,
                simulation,
                2.0,
                7.0,
                0.045,
                1000000.0
            );

        printPricingSummary(
            capletPrice,
            swaptionPrice
        );

        /*
            11. Strike sensitivity.
        */

        std::cout
            << "\nStrike Sensitivity"
            << std::endl;

        std::cout
            << "============================================================"
            << std::endl;

        std::vector<double> strikes = {
            0.035,
            0.040,
            0.045,
            0.050,
            0.055
        };

        for(double strike : strikes){

            double caplet =
                priceCapletMonteCarlo(
                    model,
                    simulation,
                    2.0,
                    strike,
                    1000000.0
                );

            double swaption =
                pricePayerSwaptionMonteCarlo(
                    model,
                    simulation,
                    2.0,
                    7.0,
                    strike,
                    1000000.0
                );

            std::cout
                << "K="
                << strike
                << ", caplet="
                << caplet
                << ", swaption="
                << swaption
                << std::endl;
        }

        /*
            12. Correlation sensitivity.
        */

        std::cout
            << "\nCorrelation Decay Sensitivity"
            << std::endl;

        std::cout
            << "============================================================"
            << std::endl;

        std::vector<double> betaValues = {
            0.05,
            0.10,
            0.30
        };

        for(double beta : betaValues){

            Matrix correlationBeta =
                exponentialCorrelationMatrix(
                    resetTimes,
                    beta
                );

            Matrix loadingsBeta =
                principalComponentLoadings(
                    correlationBeta,
                    3
                );

            GaussianLMM modelBeta(
                tenor,
                initialForwards,
                volatilityModel,
                loadingsBeta,
                initialDiscountFactors
            );

            LMMSimulationResult simulationBeta =
                simulateGaussianLMM(
                    modelBeta,
                    5.0,
                    100,
                    3000,
                    42,
                    true
                );

            double priceBeta =
                pricePayerSwaptionMonteCarlo(
                    modelBeta,
                    simulationBeta,
                    2.0,
                    7.0,
                    0.045,
                    1000000.0
                );

            std::cout
                << "beta="
                << beta
                << ", swaption price="
                << priceBeta
                << std::endl;
        }

        std::cout
            << "\nChapter 13 demonstration completed successfully."
            << std::endl;

    } catch(const std::exception& exception){

        std::cerr
            << "Error: "
            << exception.what()
            << std::endl;

        return 1;
    }

    return 0;
}
