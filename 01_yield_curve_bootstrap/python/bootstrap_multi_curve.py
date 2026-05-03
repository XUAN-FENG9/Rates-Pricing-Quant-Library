import pandas as pd
from instruments import MarketInstrument
from curve import YieldCurve

def build_ois_curve(csv_path):
    """
    Build OIS discount curve

    FO meaning:
    - Used for discounting ALL cashflows
    - Reflects collateralized funding rate
    """
    from bootstrap_single_curve import bootstrap_single_curve
    return bootstrap_single_curve(csv_path)

def build_libor_curve(csv_path):
    """
    Build a simplified LIBOR forward curve

    IMPORTANT:
    This is a simplified proxy.

    In real markets:
    - built from FRA, futures, basis swaps

    Here:
    - we approximate using IRS quotes
    """
    
    df = pd.read_csv(csv_path)
    
    instruments = [
        MarketInstrument(r['instrument'], r['tenor'], r['rate'])
        for _, r in df.iterrows() if r['instrument'] == "IRS"
    ]
    
    instruments.sort(key = lambda x: x.maturity)
    
    curve = YieldCurve()
    
    for inst in instruments:
        t = inst.maturity
        r = inst.rate
        df_val = 1/(1 + r*t)
        curve.add_df(t, df_val)
            
    return curve