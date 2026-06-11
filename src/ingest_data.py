import requests

from src.database import (
    count_observations,
    load_stations,
    save_observations,
    save_station,
)
from src.explore_api import fetch_daily_streamflow, parse_streamflow_data
from src.explore_stations import fetch_station_metadata, parse_station_metadata


# use one complete historical year for the first dashboard version
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"


# begin with a small group of Arizona stream monitoring stations
STATION_IDS = [
    "USGS-09506000",  # Verde River Near Camp Verde, AZ
    "USGS-09504000",  # Verde River Near Clarkdale, AZ
    "USGS-09498500",  # Salt River Near Roosevelt, AZ
    "USGS-09380000",  # Colorado River at Lees Ferry, AZ
]


### retrieve, clean, and store data for one monitoring station
def ingest_station(station_id: str) -> None:
    print(f"\nIngesting {station_id}...")

    metadata = fetch_station_metadata(station_id)
    station = parse_station_metadata(metadata)

    save_station(station)

    data = fetch_daily_streamflow(
        station_id=station_id,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    clean_df, rejected_df = parse_streamflow_data(data)

    if clean_df.empty:
        print("No usable observations were found.")
        return

    save_observations(clean_df)

    print("Station:", station["station_name"])
    print("Saved observations:", len(clean_df))
    print("Rejected observations:", len(rejected_df))


### ingest the selected monitoring stations without stopping after one failed request
if __name__ == "__main__":
    for station_id in STATION_IDS:
        try:
            ingest_station(station_id)
        except requests.RequestException as error:
            print("Request failed:", error)

    stations_df = load_stations()

    print("\nIngestion complete.")
    print("Stored stations:", len(stations_df))
    print("Stored observations:", count_observations())