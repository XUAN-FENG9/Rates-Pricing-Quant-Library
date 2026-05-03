import numpy as np

class LogLinearDFInterpolator:
    """
    Log-linear interpolation on discount factors.
    
    Reasoning:
    - ensures positive DF
    - produces smoother forward rates than linear DF
    """
    
    def __init__(self):
        self.times = []
        self.values = []
        
    def add(self, t, df):
        self.times.append(t)
        self.values.append(df)
        
        # Keep curve ordered (important for interpolation)
        sorted_pairs = sorted(zip(self.times, self.values))
        self.times, self.values = zip(*sorted_pairs)
        self.times = list(self.times)
        self.values = list(self.values)
        
    def get(self,t):
        if t in self.times:
            return self.values[self.times.index(t)]
        
        times = np.array(self.times)
        vals = np.array(self.values)
        
        idx = np.searchsorted(times, t)
        
        t1, t2 = times[idx-1], times[idx]
        v1, v2 = vals[idx-1], vals[idx]
        
        w = (t-t1)/(t2-t1)
        
        return np.exp((1-w)*np.log(v1) + w*np.log(v2))