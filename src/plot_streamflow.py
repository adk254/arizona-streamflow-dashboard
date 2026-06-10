import matplotlib.pyplot as plt

from src.database import load_station_observations


### plot stored streamflow observations for the verde river station
if __name__ == "__main__":
    df = load_station_observations("USGS-09506000")

    # find the observation with the highest daily mean streamflow
    peak_row = df.loc[df["streamflow_cfs"].idxmax()]

    print("Peak daily mean streamflow:")
    print(peak_row["date"].strftime("%Y-%m-%d"))
    print(peak_row["streamflow_cfs"], "ft^3/s")

    # find the two highest daily mean streamflow observations
    top_two_rows = df.nlargest(2, "streamflow_cfs")

    print("\nTwo highest daily mean streamflow observations:")
    print(top_two_rows[["date", "streamflow_cfs"]])

    # plot the daily mean streamflow observations
    fig, ax = plt.subplots()

    ax.plot(
        df["date"],
        df["streamflow_cfs"],
    )

    ax.set_title("Daily Mean Streamflow: Verde River Near Camp Verde, AZ")
    ax.set_xlabel("Date")
    ax.set_ylabel("Streamflow (ft³/s)")

    fig.tight_layout()

    # plot the same observations using a logarithmic y-axis
    log_fig, log_ax = plt.subplots()

    log_ax.plot(
        df["date"],
        df["streamflow_cfs"],
    )

    log_ax.set_yscale("log")
    log_ax.set_title(
        "Daily Mean Streamflow: Verde River Near Camp Verde, AZ\n"
        "Logarithmic Scale"
    )
    log_ax.set_xlabel("Date")
    log_ax.set_ylabel("Streamflow (ft³/s)")

    log_fig.tight_layout()

    plt.show()