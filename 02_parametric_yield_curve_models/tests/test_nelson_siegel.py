import sys
import os

# Add python source directory into Python path
# so notebook can import local modules

project_root = os.path.abspath("../python")

sys.path.append(project_root)

from nelson_siegel import NelsonSiegelCurve


def test_discount_factor_positive():

    model = NelsonSiegelCurve(
        0.03,
        -0.01,
        0.02,
        2.0
    )

    df = model.discount_factor(5.0)

    assert df > 0


def test_zero_rate_reasonable():

    model = NelsonSiegelCurve(
        0.03,
        -0.01,
        0.02,
        2.0
    )

    r = model.zero_rate(10.0)

    assert 0 < r < 0.10