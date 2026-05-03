import numpy as np
from interpolation import LogLinearDFInterpolator

class YieldCurve:
    """
    Core curve object used for pricing and risk.
    
    FO usage:
    - get_df -> discounting
    - forward_rate -> forward pricing
    - zero_rate -> curve visualization
    """
    
    def __init__(self):
        self.df_interp = LogLinearDFInterpolator()
        
    def add_df(self, t, df):
        self.df_interp.add(t, df)
        
    def get_df(self, t):
        return self.df_interp.get(t)
    
    def zero_rate(self, t):
        return -np.log(self.get_df(t))/t
    
    def forward_rate(self, t1, t2):
        """
        Forward rate implied by discount factors
        
        FO intuition:
        - market-implied future interest rate
        - very sensitive to curve smoothness
        """
        max_t = self.df_interp.times[-1]

        if t2 > max_t:
            t2 = max_t
        
        df1 = self.get_df(t1)
        df2 = self.get_df(t2)
        return (df1/df2 - 1)/(t2 - t1)
