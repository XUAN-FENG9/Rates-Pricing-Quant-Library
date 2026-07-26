#include "InterestRateTrade.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>


InterestRateSwap::InterestRateSwap(
    const std::string& tradeId,
    double notional,
    double fixedRate,
    double startTime,
    double endTime,
    bool payFixed
)
    :
    tradeId_(tradeId),
    notional_(notional),
    fixedRate_(fixedRate),
    startTime_(startTime),
    endTime_(endTime),
    payFixed_(payFixed)
{
    validate();
}


const std::string&
InterestRateSwap::tradeId() const
{
    return tradeId_;
}


double InterestRateSwap::notional() const
{
    return notional_;
}


double InterestRateSwap::fixedRate() const
{
    return fixedRate_;
}


double InterestRateSwap::startTime() const
{
    return startTime_;
}


double InterestRateSwap::endTime() const
{
    return endTime_;
}


bool InterestRateSwap::payFixed() const
{
    return payFixed_;
}


double InterestRateSwap::direction() const
{
    if (payFixed_)
    {
        return 1.0;
    }

    return -1.0;
}


void InterestRateSwap::validate() const
{
    if (tradeId_.empty())
    {
        throw std::invalid_argument(
            "tradeId cannot be empty."
        );
    }

    if (!std::isfinite(notional_) ||
        notional_ <= 0.0)
    {
        throw std::invalid_argument(
            "Swap notional must be positive."
        );
    }

    if (!std::isfinite(fixedRate_))
    {
        throw std::invalid_argument(
            "Fixed rate must be finite."
        );
    }

    if (startTime_ < 0.0)
    {
        throw std::invalid_argument(
            "Swap start time cannot be negative."
        );
    }

    if (endTime_ <= startTime_)
    {
        throw std::invalid_argument(
            "Swap end time must be after start time."
        );
    }
}


void InterestRateSwap::printSummary() const
{
    std::cout
        << "Trade ID: "
        << tradeId_
        << "\n"
        << "Notional: "
        << notional_
        << "\n"
        << "Fixed rate: "
        << fixedRate_
        << "\n"
        << "Start time: "
        << startTime_
        << "\n"
        << "End time: "
        << endTime_
        << "\n"
        << "Direction: "
        << (
            payFixed_
            ?
            "Payer fixed"
            :
            "Receiver fixed"
        )
        << "\n";
}


NettingSet::NettingSet(
    const std::string& nettingSetId
)
    :
    nettingSetId_(nettingSetId)
{
    if (nettingSetId_.empty())
    {
        throw std::invalid_argument(
            "nettingSetId cannot be empty."
        );
    }
}


NettingSet::NettingSet(
    const std::string& nettingSetId,
    const std::vector<InterestRateSwap>& trades
)
    :
    nettingSetId_(nettingSetId),
    trades_(trades)
{
    if (nettingSetId_.empty())
    {
        throw std::invalid_argument(
            "nettingSetId cannot be empty."
        );
    }
}


void NettingSet::addTrade(
    const InterestRateSwap& trade
)
{
    trades_.push_back(
        trade
    );
}


const std::string&
NettingSet::nettingSetId() const
{
    return nettingSetId_;
}


const std::vector<InterestRateSwap>&
NettingSet::trades() const
{
    return trades_;
}


std::size_t NettingSet::numberOfTrades() const
{
    return trades_.size();
}


double NettingSet::maturity() const
{
    if (trades_.empty())
    {
        return 0.0;
    }

    double result = 0.0;

    for (const InterestRateSwap& trade :
         trades_)
    {
        result = std::max(
            result,
            trade.endTime()
        );
    }

    return result;
}


void NettingSet::printSummary() const
{
    std::cout
        << "Netting Set ID: "
        << nettingSetId_
        << "\n"
        << "Number of trades: "
        << trades_.size()
        << "\n"
        << "Maturity: "
        << maturity()
        << "\n";
}
