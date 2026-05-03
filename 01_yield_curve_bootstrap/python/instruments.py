def tenor_to_years(tenor: str) -> float:
    if tenor.endswith("M"):
        return float(tenor[:-1])/12.0
    elif tenor.endswith("Y"):
        return float(tenor[:-1])
    else:
        raise ValueError("Invalid tenor")
        
class MarketInstrument:
    """
    Market instrument used for curve construction
    
    OIS -> discount curve
    IRS -> forward / long end
    """
    
    def __init__(self, typ, tenor, rate):
        self.type = typ
        self.tenor = tenor
        self.rate = float(rate)
        self.maturity = tenor_to_years(tenor)
