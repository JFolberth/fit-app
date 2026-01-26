import json
from datetime import date
import azure.functions as func

import activities


def make_request(url: str, params: dict | None = None):
    req = func.HttpRequest(method="GET", url=url, headers={}, params=params or {}, body=None)
    return req


class FakeContainer:
    def __init__(self, items):
        self.items = items
    def query_items(self, query, parameters=None, enable_cross_partition_query=False):
        p = {x['name']: x['value'] for x in (parameters or [])}
        items = list(self.items)
        if p.get('@type'):
            items = [i for i in items if i.get('type') == p['@type']]
        items.sort(key=lambda i: i.get('date', ''), reverse=True)
        limit = p.get('@limit', 50)
        return items[:limit]


def test_list_contract_filters_and_limit(monkeypatch):
    # Prepare fake data
    items = [
        {
            "id": "1",
            "type": "Running",
            "duration": 30,
            "distance": 3.1,
            "avgBpm": 140,
            "comments": "Felt good",
            "date": date(2026, 1, 20).isoformat(),
            "createdAt": "2026-01-20T12:00:00Z",
            "updatedAt": "2026-01-20T12:00:00Z",
        },
        {
            "id": "2",
            "type": "Rowing",
            "duration": 25,
            "distance": None,
            "avgBpm": 130,
            "comments": None,
            "date": date(2026, 1, 21).isoformat(),
            "createdAt": "2026-01-21T12:00:00Z",
            "updatedAt": "2026-01-21T12:00:00Z",
        },
        {
            "id": "3",
            "type": "Rucking",
            "duration": 60,
            "distance": 4.0,
            "avgBpm": 120,
            "comments": "Evening training",
            "date": date(2026, 1, 22).isoformat(),
            "createdAt": "2026-01-22T12:00:00Z",
            "updatedAt": "2026-01-22T12:00:00Z",
        },
    ]
    fake = FakeContainer(items)
    monkeypatch.setattr(activities, "_get_container", lambda: fake)

    res = activities.main(make_request("/api/activities", params={"type": "Running", "limit": "2"}))
    assert res.status_code == 200
    data = json.loads(res.get_body())
    assert isinstance(data, list)
    assert all(i["type"] == "Running" for i in data)
    # Ensure key fields are present in returned items per contract
    for i in data:
        for f in ["id", "type", "duration", "date", "createdAt", "updatedAt"]:
            assert f in i

    # Limit enforced
    res2 = activities.main(make_request("/api/activities", params={"limit": "1"}))
    data2 = json.loads(res2.get_body())
    assert len(data2) == 1
