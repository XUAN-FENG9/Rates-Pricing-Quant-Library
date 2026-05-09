import sys
import os

# Add python source directory into Python path
# so notebook can import local modules

project_root = os.path.abspath("../python")

sys.path.append(project_root)

from curve import YieldCurve
from fra import FRA


def test_fra_positive_value():

    maturities = [1, 2, 5, 10]
    rates = [0.02, 0.025, 0.03, 0.035]

    curve = YieldCurve(
        maturities,
        rates
    )

    fra = FRA(
        notional=1_000_000,
        strike=0.02,
        start=1,
        end=1.5
    )

    pv = fra.value(curve)

    assert pv > 0