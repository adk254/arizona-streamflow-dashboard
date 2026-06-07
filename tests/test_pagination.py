import src.explore_api as explore_api


# confirm that paginated api responses are combined into one response
def test_fetch_daily_streamflow_combines_pages(monkeypatch):
    page_1 = {
        "features": [
            {"id": "observation-1"},
            {"id": "observation-2"},
        ],
        "links": [
            {
                "rel": "next",
                "href": "https://example.com/page-2",
            }
        ],
        "numberReturned": 2,
    }

    page_2 = {
        "features": [
            {"id": "observation-3"},
            {"id": "observation-4"},
        ],
        "links": [
            {
                "rel": "next",
                "href": "https://example.com/page-3",
            }
        ],
        "numberReturned": 2,
    }

    page_3 = {
        "features": [
            {"id": "observation-5"},
        ],
        "links": [],
        "numberReturned": 1,
    }

    requested_urls = []

    # return a known fake response for each requested page
    def fake_fetch_streamflow_page(url: str, params: dict | None = None) -> dict:
        requested_urls.append(url)

        if url == explore_api.BASE_URL:
            return page_1

        if url == "https://example.com/page-2":
            return page_2

        if url == "https://example.com/page-3":
            return page_3

        raise ValueError(f"Unexpected url: {url}")

    monkeypatch.setattr(
        explore_api,
        "fetch_streamflow_page",
        fake_fetch_streamflow_page,
    )

    data = explore_api.fetch_daily_streamflow(
        station_id="USGS-TEST",
        start_date="2026-05-01",
        end_date="2026-05-05",
        limit=2,
    )

    assert data["numberReturned"] == 5
    assert len(data["features"]) == 5
    assert requested_urls == [
        explore_api.BASE_URL,
        "https://example.com/page-2",
        "https://example.com/page-3",
    ]