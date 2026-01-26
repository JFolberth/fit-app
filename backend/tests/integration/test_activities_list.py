import json
from datetime import date
import azure.functions as func

import activities


def make_request(url: str, params: dict | None = None):
    req = func.HttpRequest(method="GET", url=url, headers={}, params=params or {}, body=None)
    return req


class FakeContainer:
    def __init__(self):
        self.items = []
    def create_item(self, body):
        self.items.append(body)
        return body
    def query_items(self, query, parameters=None, enable_cross_partition_query=False):
        p = {x['name']: x['value'] for x in (parameters or [])}
        items = list(self.items)
        if p.get('@type'):
            items = [i for i in items if i.get('type') == p['@type']]
        items.sort(key=lambda i: i.get('date', ''), reverse=True)
        limit = p.get('@limit', 50)
        return items[:limit]


def test_list_history_with_filter_and_order(monkeypatch):
    fake = FakeContainer()
    monkeypatch.setattr(activities, "_get_container", lambda: fake)

    # Seed items via POST
    def post(payload):
        req = func.HttpRequest(method="POST", url="/api/activities", headers={}, params={}, body=json.dumps(payload).encode("utf-8"))
        return activities.main(req)

    post({"type": "Running", "duration": 30, "distance": 3.1, "avgBpm": 140, "date": date(2026, 1, 20).isoformat()})
    post({"type": "Rowing", "duration": 25, "avgBpm": 130, "date": date(2026, 1, 21).isoformat()})
    post({"type": "Rucking", "duration": 60, "distance": 4.0, "avgBpm": 120, "date": date(2026, 1, 22).isoformat()})

    # List all, order by date desc
    res_all = activities.main(make_request("/api/activities", params={"limit": "10"}))
    assert res_all.status_code == 200
    all_items = json.loads(res_all.get_body())
    dates = [i["date"] for i in all_items]
    assert dates == sorted(dates, reverse=True)

    # Filter by type
    res_running = activities.main(make_request("/api/activities", params={"type": "Running"}))
    running = json.loads(res_running.get_body())
    assert all(i["type"] == "Running" for i in running)
