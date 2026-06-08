import requests

from src.database import save_station

# USGS monitoring locations api url
BASE_URL = (
    "https://api.waterdata.usgs.gov/ogcapi/v0/"
    "collections/monitoring-locations/items"
)


### request metadata for one monitoring station from the USGS api
def fetch_station_metadata(station_id: str) -> dict:
    url = f"{BASE_URL}/{station_id}"

    params = {
        "f": "json",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


### convert the nested api response into a clean station record
def parse_station_metadata(data: dict) -> dict:
    properties = data.get("properties", {})
    coordinates = data.get("geometry", {}).get("coordinates", [])

    longitude = coordinates[0] if len(coordinates) > 0 else None
    latitude = coordinates[1] if len(coordinates) > 1 else None

    station = {
        "station_id": properties.get("id"),
        "station_name": properties.get("monitoring_location_name"),
        "state_name": properties.get("state_name"),
        "county_name": properties.get("county_name"),
        "site_type": properties.get("site_type"),
        "latitude": latitude,
        "longitude": longitude,
        "altitude_ft": properties.get("altitude"),
        "drainage_area_sqmi": properties.get("drainage_area"),
        "time_zone": properties.get("time_zone_abbreviation"),
    }

    return station


### run a small test request for the verde river near camp verde station
if __name__ == "__main__":
    data = fetch_station_metadata("USGS-09506000")
    station = parse_station_metadata(data)

    save_station(station)

    print("Clean station record:")

    for key, value in station.items():
        print(key, "->", value)