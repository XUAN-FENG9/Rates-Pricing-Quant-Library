import pandas as pd
import numpy as np
from instruments import MarketInstrument
from curve import YieldCurve

def bootstrap_single_curve(csv_path):
    """
    Build a single yield curve using both OIS and IRS instruments.

    FO interpretation:
    - This represents the "legacy" single-curve framework
    - Same curve is used for BOTH discounting and forward rates

    Steps:
    1. Use OIS for short-end discount factors
    2. Bootstrap IRS sequentially for long-end
    """
    df = pd.read_csv(csv_path)
    
    instruments = [
        MarketInstrument(r['instrument'], r['tenor'], r['rate'])
        for _, r in df.iterrows()
    ]
    
    instruments.sort(key = lambda x: x.maturity)
    
    curve = YieldCurve()
    
    # ---------------------------
    # Step 1: OIS → direct DF
    # ---------------------------
    for inst in instruments:
        if inst.type == "OIS":
            t = inst.maturity
            r = inst.rate
            df_val = np.exp(-r * t)
            curve.add_df(t, df_val)
            
    # ---------------------------
    # Step 2: IRS bootstrapping
    # ---------------------------
    for inst in instruments:
        if inst.type == "IRS":
            T = inst.maturity
            K = inst.rate
            
            alpha = 1.0
            times = np.arange(alpha, T, alpha)

            # PV of fixed leg
            fixed_leg_pv = 0.0
            known_times = set(curve.df_interp.times)
            for t in times:
                if t not in known_times:
                    continue
                fixed_leg_pv += alpha * curve.get_df(t)
         
            df_T = (1 - K * fixed_leg_pv) / (1 + K * alpha)

            curve.add_df(T, df_T)
            
    return curve
    
