from bootstrap_single_curve import bootstrap_single_curve

def test_discount_factor_monotonic():
    """
    Discount factors should decrease with maturity
    """
    curve = bootstrap_single_curve("../data/market_data_sample.csv")

    assert curve.get_df(2.0) < curve.get_df(1.0)


def test_forward_rate_positive():
    """
    Forward rates should be positive in normal market
    """
    curve = bootstrap_single_curve("../data/market_data_sample.csv")

    fwd = curve.forward_rate(1.0, 2.0)

    assert fwd > 0
    
    