import matplotlib.pyplot as plt
import numpy as np


def plot_curve(
    market_times,
    market_rates,
    model
):
    """
    Plot market vs fitted curve.
    """

    dense_times = np.linspace(
        min(market_times),
        max(market_times),
        200
    )

    fitted = [
        model.zero_rate(t)
        for t in dense_times
    ]

    plt.figure()

    plt.scatter(
        market_times,
        market_rates,
        label="Market Data"
    )

    plt.plot(
        dense_times,
        fitted,
        label="Nelson-Siegel Fit"
    )

    plt.xlabel("Maturity")
    plt.ylabel("Zero Rate")
    plt.title("Nelson-Siegel Curve Fit")

    plt.legend()
    plt.grid()

    plt.show()
