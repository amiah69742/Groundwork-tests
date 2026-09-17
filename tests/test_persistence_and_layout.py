import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_data_survives_a_reload(project):
    project.quick_add("Still here")
    project.advance("Still here", "Start")
    project.reload()
    expect(project.heading).to_have_text("Test project")
    assert project.titles_in("doing") == ["Still here"]


def test_chosen_view_is_remembered(sample):
    sample.switch_view("List")
    sample.reload()
    assert sample.active_view() == "List"


def test_corrupt_saved_data_does_not_break_the_app(app):
    """If localStorage holds junk, the app should start empty instead of crashing."""
    app.page.evaluate("localStorage.setItem('groundwork.v1', '{not json')")
    app.reload()
    expect(app.heading).to_have_text("Start with a project")


def test_phone_width_has_no_sideways_scroll(sample):
    sample.page.set_viewport_size({"width": 375, "height": 740})
    overflow = sample.page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert overflow <= 0
    expect(sample.column("done")).to_be_visible()


def test_no_javascript_errors_during_a_normal_session(page):
    from pages.groundwork_page import GroundworkPage
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    app = GroundworkPage(page).open()
    app.load_sample_project()
    for view in ["List", "Timeline", "Board"]:
        app.switch_view(view)
    app.open_task("Choose a hosting plan")
    app.save_task()
    assert errors == []
