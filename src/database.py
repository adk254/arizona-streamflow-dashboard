import sqlite3
from pathlib import Path

import pandas as pd


# store the sqlite database inside the data folder
DATABASE_PATH = Path("data/streamflow.db")


### create the observations table if it does not already exist
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