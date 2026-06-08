from src.database import load_station_observations


### inspect stored observations for the verde river station
if __name__ == "__main__":
    df = load_station_observations("USGS-09506000")

    print("Number of joined records:")
    print(len(df))

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst five records:")
    print(df.head())

    print("\nLast five records:")
    print(df.tail())