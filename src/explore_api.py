import pandas as pd
import requests

# USGS national water information system api url
BASE_URL = "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items"

### request daily streamflow observations from the USGS api
def fetch_daily_streamflow(
        station_id: str,
        start_date: str,
        end_date: str,
) -> dict:
    params = {
        "f": "json",
        "limit": 1000,
        "monitoring_location_id": station_id,
        "parameter_code": "00060",
        "statistic_id": "00003",
        "datetime": f"{start_date}/{end_date}",
    }

    response = requests.get(BASE_URL, params=params, timeout = 30)
    response.raise_for_status()

    return response.json()


### convert the nested api response into clean pandas dataframes
def parse_streamflow_data(data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    records = []

    # return empty dataframes if the api did not return any observations
    if not data.get("features"):
        return pd.DataFrame(), pd.DataFrame()

    for feature in data["features"]:
        properties = feature.get("properties", {})
        coordinates = feature.get("geometry", {}).get("coordinates", [])

        # use missing values if coordinates are incomplete
        longitude = coordinates[0] if len(coordinates) > 0 else None
        latitude = coordinates[1] if len(coordinates) > 1 else None

        record = {
            "station_id": properties.get("monitoring_location_id"),
            "date": properties.get("time"),
            "streamflow_cfs": properties.get("value"),
            "approval_status": properties.get("approval_status"),
            "longitude": longitude,
            "latitude": latitude,
        }

        records.append(record)

    df = pd.DataFrame(records)

    # convert dates and measurements into appropriate data types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["streamflow_cfs"] = pd.to_numeric(
        df["streamflow_cfs"],
        errors="coerce",
    )

    # flag records that cannot be used reliably
    invalid_rows = (
        df["station_id"].isna()
        | df["date"].isna()
        | df["streamflow_cfs"].isna()
        | df["longitude"].isna()
        | df["latitude"].isna()
    )

    rejected_df = df[invalid_rows].copy()
    clean_df = df[~invalid_rows].copy()

    # remove duplicate station-date observations
    clean_df = clean_df.drop_duplicates(
        subset=["station_id", "date"],
        keep="last",
    )

    # sort the observations chronologically and reset the row numbers
    clean_df = clean_df.sort_values(by="date").reset_index(drop=True)
    rejected_df = rejected_df.reset_index(drop=True)

    return clean_df, rejected_df


### run a small test request for the verde river near camp verde station
if __name__ == "__main__":
    data = fetch_daily_streamflow(
        station_id="USGS-09506000",
        start_date="2026-05-01",
        end_date="2026-05-07",
    )

    df, rejected_df = parse_streamflow_data(data)

    print(df)

    print("\nSummary statistics:")
    print(df["streamflow_cfs"].describe())

    print("\nRejected records:")
    print(rejected_df)

    print("\nNumber of rejected records:")
    print(len(rejected_df))