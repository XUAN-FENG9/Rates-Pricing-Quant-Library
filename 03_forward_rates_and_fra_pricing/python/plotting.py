import matplotlib.pyplot as plt


def plot_zero_curve(
    maturities,
    rates
):
    """
    Plot zero curve.
    """

    plt.figure()

    plt.plot(
        maturities,
        rates
    )

    plt.title("Zero Curve")
    plt.xlabel("Maturity")
    plt.ylabel("Zero Rate")

    plt.grid()

    plt.show()


def plot_forward_curve(
    times,
    fwds
):
    """
    Plot forward curve.
    """

    plt.figure()

    plt.plot(
        times,
        fwds
    )

    plt.title("Forward Curve")
    plt.xlabel("Start Time")
    plt.ylabel("Forward Rate")

    plt.grid()

    plt.show()