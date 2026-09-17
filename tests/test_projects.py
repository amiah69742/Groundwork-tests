import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_first_visit_shows_empty_state(app):
    expect(app.heading).to_have_text("Start with a project")
    expect(app.page.get_by_role("button", name="Create a project")).to_be_visible()


@pytest.mark.smoke
def test_create_project(project):
    expect(project.heading).to_have_text("Test project")
    assert project.sidebar_projects() == ["Test project"]


def test_project_name_is_required(app):
    app.page.locator("#newProject").click()
    app.dialog.get_by_role("button", name="Create project").click()
    expect(app.dialog).to_be_visible()  # dialog stays open, nothing created
    expect(app.page.locator("#plist .pname")).to_have_count(0)


def test_project_name_is_trimmed(app):
    app.create_project("   Padded name   ")
    expect(app.heading).to_have_text("Padded name")


def test_rename_project(project):
    project.rename_project("Renamed")
    expect(project.heading).to_have_text("Renamed")
    assert project.sidebar_projects() == ["Renamed"]


def test_delete_project_needs_a_second_click(project):
    project.delete_project(confirm=False)
    project.dialog.get_by_role("button", name="Cancel").click()
    assert project.sidebar_projects() == ["Test project"]


def test_delete_project_removes_its_tasks(project):
    project.quick_add("Doomed task")
    project.delete_project()
    expect(project.heading).to_have_text("Start with a project")
    project.create_project("Fresh start")
    expect(project.page.locator(".card")).to_have_count(0)


def test_all_projects_view_appears_with_two_projects(project):
    assert "All projects" not in project.sidebar_projects()
    project.quick_add("Task in first")
    project.create_project("Second project")
    project.quick_add("Task in second")
    assert project.sidebar_projects()[0] == "All projects"
    project.select_project("All projects")
    assert sorted(project.visible_titles()) == ["Task in first", "Task in second"]


def test_sidebar_shows_done_count(sample):
    expect(sample.page.locator("#plist .pcount")).to_have_text("2/7")
