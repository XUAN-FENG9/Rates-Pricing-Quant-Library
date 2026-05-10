import matplotlib.pyplot as plt


def plot_zero_curve(
    maturities,
    rates
):

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