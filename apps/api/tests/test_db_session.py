from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_session, get_session_factory


def test_session_factory_requires_explicit_transactions() -> None:
    first = get_session_factory()()
    second = get_session_factory()()
    try:
        assert first is not second
        assert first.autobegin is False
        assert first.expire_on_commit is False
        assert second.autobegin is False
    finally:
        first.close()
        second.close()


def test_concurrent_requests_receive_different_sessions() -> None:
    application = FastAPI()
    barrier = Barrier(2)

    @application.get("/session-id")
    def session_id(session: Annotated[Session, Depends(get_session)]) -> dict[str, int]:
        barrier.wait(timeout=5)
        return {"session_id": id(session)}

    def request_session_id() -> int:
        with TestClient(application) as client:
            response = client.get("/session-id")
            assert response.status_code == 200
            return int(response.json()["session_id"])

    with ThreadPoolExecutor(max_workers=2) as executor:
        session_ids = list(executor.map(lambda _: request_session_id(), range(2)))

    assert len(set(session_ids)) == 2
