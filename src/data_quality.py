import pandas as pd


### find expected dates that are missing from an observation dataframe
def find_missing_dates(
        df: pd.DataFrame,
        start_date: str,
        end_date: str,
) -> pd.DatetimeIndex:
    expected_dates = pd.date_range(
        start = start_date,
        end = end_date,
        freq="D",
    )

    observed_dates = pd.DatetimeIndex(
        df["date"].dropna().unique()
    )

    return expected_dates.difference(observed_dates)