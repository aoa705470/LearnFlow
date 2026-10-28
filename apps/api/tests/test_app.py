from fastapi.testclient import TestClient

from app.main import app


def test_openapi_identifies_learnflow_api() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "LearnFlow API"
    assert response.json()["paths"] == {}
