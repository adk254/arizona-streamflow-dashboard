import pandas as pd
import requests

# USGS water data api url
BASE_URL = "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items"

### request one page of daily streamflow observations from the USGS api
def fetch_streamflow_page(
        url: str,
        params: dict | None = None,
) -> dict:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()

### helper func - find the url for the next page of api results
def get_next_link(data: dict) -> str | None:
    for link in data.get("links", []):
        if link.get("rel") == "next":
            return link.get("href")

    return None

### request all pages of daily streamflow observations from the USGS api
def fetch_daily_streamflow(
        station_id: str,
        start_date: str,
        end_date: str,
        limit: int = 1000,
) -> dict:
    params = {
        "f": "json",
        "limit": limit,
        "monitoring_location_id": station_id,
        "parameter_code": "00060",
        "statistic_id": "00003",
        "datetime": f"{start_date}/{end_date}",
    }

    data = fetch_streamflow_page(BASE_URL, params=params)
    all_features = data["features"].copy()

    # follow each next link until every page has been retrieved
    next_url = get_next_link(data)
    seen_urls = set()

    while next_url:
        # stop if the api unexpectedly returns the same next link twice
        if next_url in seen_urls:
            raise RuntimeError("Repeated pagination link detected.")

        seen_urls.add(next_url)

        page_data = fetch_streamflow_page(next_url)
        all_features.extend(page_data["features"])

        next_url = get_next_link(page_data)

    # return the combined observations in the same general response structure
    data["features"] = all_features
    data["numberReturned"] = len(all_features)

    return data
        


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


### run a one-year test request for the verde river near camp verde station
if __name__ == "__main__":
    data = fetch_daily_streamflow(
        station_id="USGS-09506000",
        start_date="2025-01-01",
        end_date="2025-12-31",
    )

    df, rejected_df = parse_streamflow_data(data)

    print("Number of clean records:")
    print(len(df))

    print("\nDate range:")
    print(df["date"].min(), "to", df["date"].max())

    print("\nApproval statuses:")
    print(df["approval_status"].value_counts())

    print("\nStreamflow summary statistics:")
    print(df["streamflow_cfs"].describe())

    print("\nNumber of rejected records:")
    print(len(rejected_df))