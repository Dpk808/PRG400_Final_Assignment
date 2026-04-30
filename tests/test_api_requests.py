def test_create_request_requires_login(client):
    resp = client.post("/api/requests", json={"book_id": 1})
    assert resp.status_code in {302, 401}


def test_create_request_as_student(client):
    client.post(
        "/login",
        data={"username": "student1", "password": "pass123"},
        follow_redirects=True,
    )
    resp = client.post("/api/requests", json={"book_id": 1})
    assert resp.status_code == 201
    payload = resp.get_json()
    assert payload["status"] == "pending"
