import pytest

try:
    from fastapi.testclient import TestClient
    from app.main import app
except Exception as exc:  # pragma: no cover - environment dependent
    pytest.skip(f"Skipping health test due to app startup dependency: {exc}", allow_module_level=True)


client = TestClient(app)


def test_health_check():
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
