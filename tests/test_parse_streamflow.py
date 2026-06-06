from src.explore_api import parse_streamflow_data


# create a small fake api response for testing
def make_test_data() -> dict:
    return {
        "features": [
            {
                "properties": {
                    "monitoring_location_id": "USGS-TEST",
                    "time": "2026-05-01",
                    "value": "85.3",
                    "approval_status": "Provisional",
                },
                "geometry": {
                    "coordinates": [-111.79, 34.45],
                },
            },
            {
                "properties": {
                    "monitoring_location_id": "USGS-TEST",
                    "time": "2026-05-02",
                    "value": "not available",
                    "approval_status": "Provisional",
                },
                "geometry": {
                    "coordinates": [-111.79, 34.45],
                },
            },
        ]
    }


# confirm that malformed measurements are rejected without crashing
def test_invalid_streamflow_value_is_rejected():
    data = make_test_data()

    clean_df, rejected_df = parse_streamflow_data(data)

    # one valid record survives and one malformed record is rejected
    assert len(clean_df) == 1
    assert len(rejected_df) == 1

    # the valid measurement is converted int a number correctly
    assert clean_df.iloc[0]["streamflow_cfs"] == 85.3

    # checks the malformed record ends up in the rejected table
    assert rejected_df.iloc[0]["date"].strftime("%Y-%m-%d") == "2026-05-02"

# confirm that an empty api response returns empty dataframes
def test_empty_response_returns_empty_dataframes():
    empty_data = {"features": []}

    clean_df, rejected_df = parse_streamflow_data(empty_data)

    assert clean_df.empty
    assert rejected_df.empty

# confirm that duplicate stateion-date records are reduced to one row
def test_duplicate_observations_are_removed():
    data = {
        "features": [
            {
                "properties": {
                    "monitoring_location_id": "USGS-TEST",
                    "time": "2026-05-01",
                    "value": "82.0",
                    "approval_status": "Provisional",
                },
                "geometry": {
                    "coordinates": [-111.79, 34.45],
                },
            },
            {
                "properties": {
                    "monitoring_location_id": "USGS-TEST",
                    "time": "2026-05-01",
                    "value": "85.0",
                    "approval_status": "Approved",
                },
                "geometry": {
                    "coordinates": [-111.79, 34.45],
                },
            },
        ]
    }

    clean_df, rejected_df = parse_streamflow_data(data)

    assert len(clean_df) == 1
    assert len(rejected_df) == 0
    assert clean_df.iloc[0]["streamflow_cfs"] == 85.0
    assert clean_df.iloc[0]["approval_status"] == "Approved"