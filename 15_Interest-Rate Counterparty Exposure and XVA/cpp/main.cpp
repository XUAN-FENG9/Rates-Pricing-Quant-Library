#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

#include "ExposureEngine.hpp"
#include "ExposureMetrics.hpp"
#include "InterestRateTrade.hpp"
#include "XVAAdjustments.hpp"


// ============================================================
// Chapter 13 Gaussian LMM headers
// ============================================================

#include "../../13_gaussain_libor_market_model_lmm/cpp/Correlation.hpp"

#include "../../13_gaussain_libor_market_model_lmm/cpp/GaussianLMM.hpp"

#include "../../13_gaussain_libor_market_model_lmm/cpp/GaussianLMMVolatility.hpp"

#include "../../13_gaussain_libor_market_model_lmm/cpp/LMMSimulation.hpp"

#include "../../13_gaussain_libor_market_model_lmm/cpp/TenorStructure.hpp"

#include "../../13_gaussain_libor_market_model_lmm/cpp/ZeroCurve.hpp"


int main()
{
    try
    {
        std::cout
            << std::fixed
            << std::setprecision(
                8
            );


        // ====================================================
        // 1. Build the initial zero curve
        //
        // This is the same market curve used by Chapter 13.
        // ====================================================

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


        // ====================================================
        // 2. Build the semiannual tenor structure
        // ====================================================

        TenorStructure tenor(
            0.0,
            10.0,
            2
        );


        std::vector<double> tenorTimes =
            tenor.times();


        std::vector<double> accruals =
            tenor.accruals();


        std::vector<double> initialForwards =
            tenor.initialForwardRates(
                curve
            );


        std::vector<double> initialDiscountFactors =
            tenor.initialDiscountFactors(
                curve
            );


        std::cout
            << "Tenor dates: "
            << tenorTimes.size()
            << "\n";

        std::cout
            << "Initial forwards: "
            << initialForwards.size()
            << "\n";

        std::cout
            << "Accrual periods: "
            << accruals.size()
            << "\n";


        // ====================================================
        // 3. Construct forward reset times
        //
        // tenorTimes contains:
        //
        // T_0, T_1, ..., T_N
        //
        // resetTimes contains:
        //
        // T_0, T_1, ..., T_{N-1}
        // ====================================================

        std::vector<double> resetTimes(
            tenor.times().begin(),
            tenor.times().end() - 1
        );


        if (
            resetTimes.size()
            !=
            initialForwards.size()
        )
        {
            throw std::runtime_error(
                "Reset-time dimension does not match "
                "the forward-rate dimension."
            );
        }


        // ====================================================
        // 4. Build the Chapter 13 correlation matrix
        // ====================================================

        Matrix correlationMatrix =
            exponentialCorrelationMatrix(
                resetTimes,
                0.10
            );


        // ====================================================
        // 5. Reduce the correlation matrix to three PCA factors
        // ====================================================

        Matrix correlationLoadings =
            principalComponentLoadings(
                correlationMatrix,
                3
            );


        // ====================================================
        // 6. Build the Gaussian normal-volatility model
        //
        // sigmaLevel = 0.01:
        // approximately 100 basis points of normal volatility
        // ====================================================

        GaussianLMMVolatility volatilityModel(
            resetTimes,
            0.01,
            0.05,
            0.001
        );


        // ====================================================
        // 7. Build the Chapter 13 Gaussian LMM
        //
        // The exact constructor order is:
        //
        // tenor
        // initial forwards
        // volatility model
        // PCA correlation loadings
        // initial discount factors
        // ====================================================

        GaussianLMM model(
            tenor,
            initialForwards,
            volatilityModel,
            correlationLoadings,
            initialDiscountFactors
        );


        std::cout
            << "\nGaussian LMM constructed successfully."
            << "\n";

        std::cout
            << "Number of forwards: "
            << model.numberOfForwards()
            << "\n";

        std::cout
            << "Number of factors: "
            << model.numberOfFactors()
            << "\n";


        // ====================================================
        // 8. Call the real Chapter 13 Gaussian LMM simulator
        // ====================================================

        double simulationEnd =
            7.0;


        int numberOfSteps =
            140;


        int numberOfPaths =
            3000;


        unsigned int seed =
            42;


        bool antithetic =
            true;


        LMMSimulationResult chapter13Simulation =
            simulateGaussianLMM(
                model,
                simulationEnd,
                numberOfSteps,
                numberOfPaths,
                seed,
                antithetic
            );


        std::cout
            << "\nChapter 13 simulation completed."
            << "\n";

        std::cout
            << "Simulation times: "
            << chapter13Simulation.times.size()
            << "\n";

        std::cout
            << "Simulation paths: "
            << chapter13Simulation.forwardPaths.size()
            << "\n";


        if (
            chapter13Simulation.forwardPaths.empty()
        )
        {
            throw std::runtime_error(
                "Chapter 13 returned no simulation paths."
            );
        }


        if (
            chapter13Simulation
                .forwardPaths
                .front()
                .empty()
        )
        {
            throw std::runtime_error(
                "Chapter 13 returned no simulation times."
            );
        }


        std::cout
            << "Forwards per state: "
            << chapter13Simulation
                .forwardPaths
                .front()
                .front()
                .size()
            << "\n";


        // ====================================================
        // 9. Adapt Chapter 13 output to Chapter 15
        //
        // No new simulation is performed here.
        //
        // Chapter 15 consumes the exact paths generated by
        // Chapter 13.
        // ====================================================

        ForwardSimulationResult simulation;


        simulation.times =
            chapter13Simulation.times;


        simulation.forwardPaths =
            chapter13Simulation.forwardPaths;


        std::cout
            << "\nChapter 15 simulation adapter"
            << "\n";

        std::cout
            << "Paths: "
            << simulation.numberOfPaths()
            << "\n";

        std::cout
            << "Times: "
            << simulation.numberOfTimes()
            << "\n";

        std::cout
            << "Forwards: "
            << simulation.numberOfForwards()
            << "\n";


        // ====================================================
        // 10. Define two interest-rate swaps
        // ====================================================

        InterestRateSwap payerSwap(
            "IRS_PAYER_001",
            10000000.0,
            0.045,
            0.0,
            5.0,
            true
        );


        InterestRateSwap receiverSwap(
            "IRS_RECEIVER_001",
            6000000.0,
            0.047,
            1.0,
            7.0,
            false
        );


        // ====================================================
        // 11. Add both swaps to one netting set
        // ====================================================

        NettingSet nettingSet(
            "COUNTERPARTY_A"
        );


        nettingSet.addTrade(
            payerSwap
        );


        nettingSet.addTrade(
            receiverSwap
        );


        std::cout
            << "\n";

        nettingSet.printSummary();


        // ====================================================
        // 12. Select exposure dates
        //
        // Exposure dates must appear on both:
        //
        // the LMM simulation grid
        // and
        // the tenor grid
        // ====================================================

        std::vector<double> exposureTimes =
            buildExposureTimes(
                tenorTimes,
                simulation.times,
                nettingSet.maturity()
            );


        std::cout
            << "\nExposure dates: "
            << exposureTimes.size()
            << "\n";


        std::cout
            << "Exposure grid: "
            << "\n";


        for (
            double exposureTime :
            exposureTimes
        )
        {
            std::cout
                << exposureTime
                << " ";
        }


        std::cout
            << "\n";


        // ====================================================
        // 13. Revalue every swap along every Chapter 13 path
        // ====================================================

        ExposureSimulationResult exposure =
            simulatePortfolioValues(
                tenorTimes,
                accruals,
                simulation,
                nettingSet,
                exposureTimes
            );


        std::cout
            << "\nExposure simulation completed."
            << "\n";

        std::cout
            << "Exposure paths: "
            << exposure.numberOfPaths()
            << "\n";

        std::cout
            << "Exposure times: "
            << exposure.numberOfTimes()
            << "\n";

        std::cout
            << "Trades: "
            << exposure.numberOfTrades()
            << "\n";


        // ====================================================
        // 14. Calculate EE, ENE, EPE, and PFE
        // ====================================================

        ExposureMetricsResult metrics =
            calculateExposureMetrics(
                exposure.exposureTimes,
                exposure.portfolioValues,
                0.95
            );


        metrics.printProfile();


        std::cout
            << "\n";


        metrics.printSummary();


        // ====================================================
        // 15. Define counterparty and bank credit curves
        // ====================================================

        CreditCurve counterpartyCurve(
            0.020,
            0.40
        );


        CreditCurve bankCurve(
            0.012,
            0.40
        );


        // ====================================================
        // 16. Calculate CVA, DVA, and simplified FVA
        // ====================================================

        XVAResult xva =
            calculateXVA(
                tenorTimes,
                initialDiscountFactors,
                metrics,
                counterpartyCurve,
                bankCurve,
                0.012,
                0.003
            );


        xva.printSummary();


        // ====================================================
        // 17. Calculate XVA-adjusted portfolio value
        // ====================================================

        double initialPortfolioValue =
            exposure
                .portfolioValues
                .front()
                .front();


        double adjustedPortfolioValue =
            initialPortfolioValue
            +
            xva.netValuationAdjustment;


        std::cout
            << "\nInitial portfolio value: "
            << initialPortfolioValue
            << "\n";


        std::cout
            << "Net valuation adjustment: "
            << xva.netValuationAdjustment
            << "\n";


        std::cout
            << "XVA-adjusted portfolio value: "
            << adjustedPortfolioValue
            << "\n";


        return 0;
    }
    catch (
        const std::exception& error
    )
    {
        std::cerr
            << "Error: "
            << error.what()
            << "\n";


        return 1;
    }
}
