import matplotlib.pyplot as plt
import streamlit as st

from src.database import load_station_observations


# use the verde river station for the first dashboard version
STATION_ID = "USGS-09506000"


### configure the browser tab and page layout
st.set_page_config(
    page_title="Arizona Streamflow Explorer",
    page_icon="💧",
    layout="wide",
)


### load stored observations from the local sqlite database
df = load_station_observations(STATION_ID)

if df.empty:
    st.error("No stored observations were found for this station.")
    st.stop()


### calculate dashboard summary values
station_name = df.iloc[0]["station_name"]
state_name = df.iloc[0]["state_name"]
county_name = df.iloc[0]["county_name"]
site_type = df.iloc[0]["site_type"]

latest_row = df.iloc[-1]
peak_row = df.loc[df["streamflow_cfs"].idxmax()]
average_streamflow = df["streamflow_cfs"].mean()


### page header
st.title("Arizona Streamflow Explorer")

st.write(
    "Explore stored daily mean streamflow observations from "
    "U.S. Geological Survey monitoring stations."
)

st.subheader(station_name)

st.caption(
    f"{site_type} monitoring station | "
    f"{county_name}, {state_name} | "
    f"Station ID: {STATION_ID}"
)


### add a sidebar control for the graph scale
with st.sidebar:
    st.header("Display options")

    y_axis_scale = st.radio(
        "Y-axis scale",
        options=["Linear", "Logarithmic"],
    )


### display summary metrics in one row
metric_1, metric_2, metric_3, metric_4 = st.columns(4)

metric_1.metric(
    "Latest daily mean",
    f"{latest_row['streamflow_cfs']:,.1f} ft³/s",
)

metric_2.metric(
    "Average daily mean",
    f"{average_streamflow:,.1f} ft³/s",
)

metric_3.metric(
    "Peak daily mean",
    f"{peak_row['streamflow_cfs']:,.1f} ft³/s",
)

metric_4.metric(
    "Stored observations",
    f"{len(df):,}",
)


### plot stored daily mean streamflow observations
fig, ax = plt.subplots(figsize=(10, 4.5))

ax.plot(
    df["date"],
    df["streamflow_cfs"],
)

if y_axis_scale == "Logarithmic":
    ax.set_yscale("log")

ax.set_title("Daily Mean Streamflow")
ax.set_xlabel("Date")
ax.set_ylabel("Streamflow (ft³/s)")

fig.tight_layout()

st.pyplot(fig, width="stretch")


### show additional context about the peak observation
st.caption(
    "Peak stored daily mean streamflow: "
    f"{peak_row['streamflow_cfs']:,.1f} ft³/s on "
    f"{peak_row['date'].strftime('%Y-%m-%d')}."
)


### allow users to inspect the stored data
with st.expander("View stored observations"):
    st.dataframe(
        df[
            [
                "date",
                "streamflow_cfs",
                "approval_status",
            ]
        ],
        hide_index=True,
        width="stretch",
    )