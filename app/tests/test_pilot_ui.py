from pathlib import Path


WEB = Path(__file__).resolve().parent.parent / "web"


def test_public_ui_has_custom_queue_and_never_calls_global_reset():
    html = (WEB / "index.html").read_text(encoding="utf-8")
    js = (WEB / "app.js").read_text(encoding="utf-8")
    pilot = (WEB / "pilot.js").read_text(encoding="utf-8")
    assert "New incident" in html and 'id="incident-select"' in html
    assert 'id="incident-dialog"' in html and "/api/pilot/readiness" in html
    assert "/api/reset" not in js + pilot
    assert "For judges" not in html and "Judge brief" not in html
