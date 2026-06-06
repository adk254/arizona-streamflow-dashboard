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


### convert the nested api response into a pandas dataframe
def parse_streamflow_data(data: dict) -> pd.DataFrame:
    records = []

    for feature in data["features"]:
        properties = feature["properties"]
        longitude, latitude = feature["geometry"]["coordinates"]

        record = {
            "station_id": properties["monitoring_location_id"],
            "date": properties["time"],
            "streamflow_cfs": float(properties["value"]),
            "approval_status": properties["approval_status"],
            "longitude": longitude,
            "latitude": latitude,
        }

        records.append(record)

    df = pd.DataFrame(records)

    # sort the observations chronologically and reset the row numbers
    df = df.sort_values(by="date").reset_index(drop=True)

    return df


# run a small test request for the verde river near camp verde station
if __name__ == "__main__":
    data = fetch_daily_streamflow(
        station_id="USGS-09506000",
        start_date="2026-05-01",
        end_date="2026-05-07",
    )

    df = parse_streamflow_data(data)

    print(df)

    print("\nSummary statistics:")
    print(df["streamflow_cfs"].describe())