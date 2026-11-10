"""EML offer and master-action diagram (lane F4). Playwright; skipped when absent."""
import urllib.request

import pytest

BASE = "http://127.0.0.1:8000"
URL = BASE + "/Pages/formulas.html"
sync_api = pytest.importorskip("playwright.sync_api")


def _server_up() -> bool:
    """True when the preview server answers for the formulas page."""
    try:
        return urllib.request.urlopen(URL, timeout=2).status == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _server_up(), reason="preview server not running")


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as exc:
            pytest.skip("chromium unavailable: %s" % exc)
        yield b
        b.close()


@pytest.fixture()
def page(browser):
    pg = browser.new_page(viewport={"width": 1366, "height": 900})
    pg.errors = []
    # Console errors from other scripts (pm-validation-stats probes) are not this lane's.
    pg.on("console", lambda m: pg.errors.append(m.text) if m.type == "error"
          and "pm-validation-stats" not in (m.location.get("url") or "") else None)
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(URL)
    pg.wait_for_selector("#master-action-host svg", timeout=30000)
    yield pg
    pg.close()


def test_withheld_formula_has_no_eml_control(page):
    for fid in ("ckm-overlap-integral", "gut-scale", "euler-characteristic"):
        card = page.locator("#formula-%s" % fid)
        if card.count():
            assert card.locator('.math-toggle-btn[data-mode="eml"]').count() == 0, fid


def test_diagram_has_nodes_and_toggle_collapses(page):
    host = page.locator("#master-action-host")
    before = host.locator("svg g[role=button]").count()
    assert before >= 4 and host.locator("svg circle").count() >= 8
    host.locator("svg g[role=button]").nth(1).press("Enter")
    after = host.locator("svg g[role=button][aria-expanded=true]").count()
    assert after < before
    assert host.locator("svg g[aria-expanded=false]").count() == 1


def test_stat_tiles_and_gate_optgroup(page):
    assert int(page.inner_text("#stat-validated")) > 0
    assert int(page.inner_text("#stat-predictions")) > 0
    assert page.locator("#section-filter optgroup").count() == 1


def test_no_console_errors(page):
    mine = [e for e in page.errors if "404" not in e and "PM_STATS" not in e]
    assert mine == []
