import matplotlib.pyplot as plt


def plot_vol_smile(
    strikes,
    vols
):

    plt.figure()

    plt.plot(
        strikes,
        vols
    )

    plt.title(
        "Swaption Volatility Smile"
    )

    plt.xlabel(
        "Strike"
    )

    plt.ylabel(
        "Implied Volatility"
    )

    plt.grid()

    plt.show()