def test_homepage(client):
    assert client.get('/').status_code == 200
