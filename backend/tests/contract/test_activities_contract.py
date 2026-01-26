import json
from datetime import date
import azure.functions as func

import activities


def make_request(method: str, url: str, body: dict | None = None, params: dict | None = None, route_params: dict | None = None):
    req = func.HttpRequest(
        method=method,
        url=url,
        headers={},
        params=params or {},
        body=(json.dumps(body).encode("utf-8") if body is not None else None),
    )
    if route_params:
        setattr(req, "route_params", route_params)
    return req


class FakeContainer:
    def __init__(self):
        self.items = []
    def create_item(self, body):
        self.items.append(body)
        return body
    def query_items(self, query, parameters=None, enable_cross_partition_query=False):
        # Contract test focuses on structure; support id lookup
        if parameters:
            p = {x['name']: x['value'] for x in parameters}
            if '@id' in p:
                return [i for i in self.items if i.get('id') == p['@id']]
        return list(self.items)
    def replace_item(self, item, body, partition_key=None):
        for idx, i in enumerate(self.items):
            if i.get('id') == item:
                self.items[idx] = body
                return body
        raise KeyError('Item not found')
    def delete_item(self, item, partition_key=None):
        self.items = [i for i in self.items if i.get('id') != item]


def test_post_activity_created_contract(monkeypatch):
    fake = FakeContainer()
    monkeypatch.setattr(activities, "_get_container", lambda: fake)

    payload = {
        "type": "Running",
        "duration": 30,
        "distance": 3.1,
        "avgBpm": 140,
        "comments": "Felt good",
        "date": date.today().isoformat(),
    }
    req = make_request("POST", "/api/activities", body=payload)
    res = activities.main(req)
    assert res.status_code == 201
    data = json.loads(res.get_body())
    # Contract assertions
    for field in ["id", "type", "duration", "date", "createdAt", "updatedAt"]:
        assert field in data


def test_post_activity_rowing_distance_invalid(monkeypatch):
    fake = FakeContainer()
    monkeypatch.setattr(activities, "_get_container", lambda: fake)

    payload = {
        "type": "Rowing",
        "duration": 20,
        "distance": 2.0,
        "avgBpm": 130,
        "date": date.today().isoformat(),
    }
    req = make_request("POST", "/api/activities", body=payload)
    res = activities.main(req)
    assert res.status_code == 400
