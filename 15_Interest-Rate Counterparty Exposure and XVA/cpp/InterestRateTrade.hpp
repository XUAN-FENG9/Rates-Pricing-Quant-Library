#ifndef INTERESTRATETRADE_H_INCLUDED
#define INTERESTRATETRADE_H_INCLUDED

#include <cstddef>
#include <string>
#include <vector>


class InterestRateSwap
{
public:

    InterestRateSwap(
        const std::string& tradeId,
        double notional,
        double fixedRate,
        double startTime,
        double endTime,
        bool payFixed
    );

    const std::string& tradeId() const;

    double notional() const;

    double fixedRate() const;

    double startTime() const;

    double endTime() const;

    bool payFixed() const;

    double direction() const;

    void validate() const;

    void printSummary() const;


private:

    std::string tradeId_;

    double notional_;

    double fixedRate_;

    double startTime_;

    double endTime_;

    bool payFixed_;
};


class NettingSet
{
public:

    NettingSet(
        const std::string& nettingSetId
    );

    NettingSet(
        const std::string& nettingSetId,
        const std::vector<InterestRateSwap>& trades
    );

    void addTrade(
        const InterestRateSwap& trade
    );

    const std::string& nettingSetId() const;

    const std::vector<InterestRateSwap>& trades() const;

    std::size_t numberOfTrades() const;

    double maturity() const;

    void printSummary() const;


private:

    std::string nettingSetId_;

    std::vector<InterestRateSwap> trades_;
};

#endif // INTERESTRATETRADE_H_INCLUDED
