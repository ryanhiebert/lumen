import pytest
import lumen


@pytest.fixture
def app():
    return lumen.app


def test_homepage(client):
    assert client.get("/").status_code == 200
