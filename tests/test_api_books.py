def test_list_books(client):
    resp = client.get("/api/books")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert isinstance(payload, list)
    assert payload[0]["title"] == "Test Book"


def test_get_book_by_id(client):
    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["id"] == 1
    assert payload["author"] == "Test Author"
