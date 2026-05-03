import pandas as pd
from bootstrap_single_curve import bootstrap_single_curve

def dv01(csv_path, maturity = 5.0):
    """
    Compute DV01 via parallel shift

    Definition:
    DV01 = change in PV when rates move +1bp

    Method:
    1. Build base curve
    2. Bump all rates by +1bp
    3. Rebuild curve
    4. Compare PV

    FO insight:
    - Measures parallel curve sensitivity
    - Real desks use bucket DV01 (more granular)
    """
    base_curve = bootstrap_single_curve(csv_path)
    
    df = pd.read_csv(csv_path)
    df['rate'] += 0.0001
    
    tmp = "tmp.csv"
    df.to_csv(tmp, index = False)
    
    bumped = bootstrap_single_curve(tmp)
    
    return bumped.get_df(maturity) - base_curve.get_df(maturity)