import sqlite3
from pathlib import Path

import pandas as pd


# store the sqlite database inside the data folder
DATABASE_PATH = Path("data/streamflow.db")


### create the database tables if they do not already exist
def create_database(database_path: Path = DATABASE_PATH) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS observations (
                station_id TEXT NOT NULL,
                date TEXT NOT NULL,
                streamflow_cfs REAL NOT NULL,
                approval_status TEXT,
                PRIMARY KEY (station_id, date)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stations (
                station_id TEXT PRIMARY KEY,
                station_name TEXT NOT NULL,
                state_name TEXT,
                county_name TEXT,
                site_type TEXT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                altitude_ft REAL,
                drainage_area_sqmi REAL,
                time_zone TEXT
            )
            """
        )


### insert or update streamflow observations in the database
def save_observations(
        df: pd.DataFrame,
        database_path: Path = DATABASE_PATH,
) -> None:
    create_database(database_path)

    records = df[
        [
            "station_id",
            "date",
            "streamflow_cfs",
            "approval_status",
        ]
    ].copy()

    # convert pandas timestamps into text that sqlite can store consistently
    records["date"] = records["date"].dt.strftime("%Y-%m-%d")

    with sqlite3.connect(database_path) as connection:
        connection.executemany(
            """
            INSERT INTO observations (
                station_id,
                date,
                streamflow_cfs,
                approval_status
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(station_id, date) DO UPDATE SET
                streamflow_cfs = excluded.streamflow_cfs,
                approval_status = excluded.approval_status
            """,
            records.itertuples(index=False, name=None),
        )


### insert or update station metadata in the database
def save_station(
        station: dict,
        database_path: Path = DATABASE_PATH,
) -> None:
    create_database(database_path)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO stations (
                station_id,
                station_name,
                state_name,
                county_name,
                site_type,
                latitude,
                longitude,
                altitude_ft,
                drainage_area_sqmi,
                time_zone
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(station_id) DO UPDATE SET
                station_name = excluded.station_name,
                state_name = excluded.state_name,
                county_name = excluded.county_name,
                site_type = excluded.site_type,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                altitude_ft = excluded.altitude_ft,
                drainage_area_sqmi = excluded.drainage_area_sqmi,
                time_zone = excluded.time_zone
            """,
            (
                station["station_id"],
                station["station_name"],
                station["state_name"],
                station["county_name"],
                station["site_type"],
                station["latitude"],
                station["longitude"],
                station["altitude_ft"],
                station["drainage_area_sqmi"],
                station["time_zone"],
            ),
        )


### count the number of stored observations
def count_observations(
        database_path: Path = DATABASE_PATH,
) -> int:
    create_database(database_path)

    with sqlite3.connect(database_path) as connection:
        result = connection.execute(
            """
            SELECT COUNT(*) 
            FROM observations
            """
        ).fetchone()

    return result[0]


### retrieve observations with their station metadata
def load_station_observations(
        station_id: str,
        database_path: Path = DATABASE_PATH,
) -> pd.DataFrame:
    create_database(database_path)

    with sqlite3.connect(database_path) as connection:
        query = """
            SELECT
                stations.station_id,
                stations.station_name,
                stations.state_name,
                stations.county_name,
                stations.site_type,
                stations.latitude,
                stations.longitude,
                observations.date,
                observations.streamflow_cfs,
                observations.approval_status
            FROM observations
            INNER JOIN stations
                ON observations.station_id = stations.station_id
            WHERE stations.station_id = ?
            ORDER BY observations.date
        """

        df = pd.read_sql_query(
            query, 
            connection, 
            params=(station_id,)
        )

        df["date"] = pd.to_datetime(df["date"])

        return df