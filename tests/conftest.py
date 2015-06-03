import pytest
import lumen.serve

@pytest.fixture
def app():
    return lumen.serve.app
