import numpy as np

def price_swap(ois_curve, libor_curve, maturity, fixed_rate):
    """
    Multi-curve IRS pricing

    FO logic:
    - Discount using OIS curve
    - Forward rates from LIBOR curve

    Parameters:
    maturity: integer (years)
    fixed_rate: swap fixed leg rate

    Returns:
    PV of swap (receiver - payer convention)
    """
    times = np.arange(1, maturity+1)
    
    fixed_leg = 0
    float_leg = 0
    
    for i, t in enumerate(times):
        
        df = ois_curve.get_df(t)
        
        fixed_leg += fixed_rate * df
        
        t_prev = 0 if i==0 else times[i-1]
        
        fwd = libor_curve.forward_rate(t_prev, t)
        
        float_leg += fwd * df
        
    return float_leg - fixed_leg