from src.data_quality import find_missing_dates
from src.database import load_station_observations, load_stations
from src.ingest_data import END_DATE, START_DATE


### report missing dates for each stored monitoring station
if __name__ == "__main__":
    stations_df = load_stations()

    for station in stations_df.itertuples(index=False):
        df = load_station_observations(station.station_id)

        missing_dates = find_missing_dates(
            df=df,
            start_date=START_DATE,
            end_date=END_DATE,
        )

        print("\nStation:", station.station_name)
        print("Stored observations:", len(df))
        print("Missing dates:", len(missing_dates))

        for date in missing_dates:
            print("-", date.strftime("%Y-%m-%d"))