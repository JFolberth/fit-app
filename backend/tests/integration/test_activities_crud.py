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
        if query.startswith("SELECT * FROM c WHERE c.id = @id"):
            p = {x['name']: x['value'] for x in (parameters or [])}
            return [i for i in self.items if i.get('id') == p.get('@id')]
        # List path: type filter + limit; emulate simply
        p = {x['name']: x['value'] for x in (parameters or [])}
        items = list(self.items)
        if p.get('@type'):
            items = [i for i in items if i.get('type') == p['@type']]
        items.sort(key=lambda i: i.get('date', ''), reverse=True)
        limit = p.get('@limit', 50)
        return items[:limit]
    def replace_item(self, item, body, partition_key=None):
        for idx, i in enumerate(self.items):
            if i.get('id') == item:
                self.items[idx] = body
                return body
        raise KeyError('Item not found')
    def delete_item(self, item, partition_key=None):
        self.items = [i for i in self.items if i.get('id') != item]


def test_crud_flow(monkeypatch):
    fake = FakeContainer()
    monkeypatch.setattr(activities, "_get_container", lambda: fake)

    # Create
    payload = {
        "type": "Rucking",
        "duration": 60,
        "distance": 4.0,
        "avgBpm": 120,
        "date": date.today().isoformat(),
    }
    res_create = activities.main(make_request("POST", "/api/activities", body=payload))
    assert res_create.status_code == 201
    created = json.loads(res_create.get_body())

    # Update
    update_payload = {"comments": "Evening training"}
    res_update = activities.main(make_request("PUT", f"/api/activities/{created['id']}", body=update_payload))
    assert res_update.status_code == 200
    updated = json.loads(res_update.get_body())
    assert updated["comments"] == "Evening training"

    # List
    res_list = activities.main(make_request("GET", "/api/activities", params={"type": "Rucking", "limit": "10"}))
    assert res_list.status_code == 200
    listed = json.loads(res_list.get_body())
    assert any(i["id"] == created["id"] for i in listed)

    # Delete
    res_delete = activities.main(make_request("DELETE", f"/api/activities/{created['id']}"))
    assert res_delete.status_code == 204
