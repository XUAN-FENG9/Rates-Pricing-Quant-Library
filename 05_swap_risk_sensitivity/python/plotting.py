import matplotlib.pyplot as plt


def plot_curve(
    maturities,
    rates,
    title
):

    plt.figure()

    plt.plot(
        maturities,
        rates
    )

    plt.title(title)

    plt.xlabel("Maturity")

    plt.ylabel("Rate")

    plt.grid()

    plt.show()