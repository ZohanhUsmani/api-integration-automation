from src.webhook import create_app


def test_health():
    app = create_app()
    c = app.test_client()
    r = c.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"