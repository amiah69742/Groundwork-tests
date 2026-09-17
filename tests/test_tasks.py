import pytest
from playwright.sync_api import expect

from tests.conftest import days_from_today


@pytest.mark.smoke
def test_quick_add_lands_in_to_do(project):
    project.quick_add("Buy supplies")
    assert project.titles_in("todo") == ["Buy supplies"]


def test_quick_add_ignores_blank_input(project):
    project.quick_add("    ")
    expect(project.page.locator(".card")).to_have_count(0)


def test_quick_add_keeps_order(project):
    for title in ["First", "Second", "Third"]:
        project.quick_add(title)
    assert project.titles_in("todo") == ["First", "Second", "Third"]


def test_add_task_with_details(project):
    project.add_task("Call the supplier", status="Doing", priority="High",
                     due=days_from_today(1), steps=["Find number", "Ask for quote"])
    card = project.card("Call the supplier")
    assert project.titles_in("doing") == ["Call the supplier"]
    expect(card).to_contain_text("Due tomorrow")
    expect(card).to_contain_text("0 of 2 steps")
    expect(card.locator(".tag")).to_have_text("High")


def test_task_title_is_required(project):
    project.page.get_by_role("button", name="Add task").click()
    project.save_task()
    expect(project.dialog).to_be_visible()
    expect(project.page.locator(".card")).to_have_count(0)


def test_edit_task_title(project):
    project.quick_add("Old title")
    project.open_task("Old title")
    project.dialog.locator("#f-title").fill("New title")
    project.save_task()
    assert project.titles_in("todo") == ["New title"]


def test_cancel_discards_edits(project):
    project.quick_add("Keep me")
    project.open_task("Keep me")
    project.dialog.locator("#f-title").fill("Changed")
    project.dialog.get_by_role("button", name="Cancel").click()
    assert project.titles_in("todo") == ["Keep me"]


def test_delete_task(project):
    project.quick_add("Temporary")
    project.open_task("Temporary")
    project.delete_open_task()
    expect(project.page.locator(".card")).to_have_count(0)


def test_ticking_a_checklist_step_updates_the_card(project):
    project.add_task("Pack", steps=["Boxes", "Tape"])
    project.open_task("Pack")
    project.dialog.get_by_label("Boxes", exact=True).check()
    project.save_task()
    expect(project.card("Pack")).to_contain_text("1 of 2 steps")


def test_start_after_due_is_swapped(project):
    """Entering the dates backwards shouldn't produce a negative-length task."""
    project.add_task("Backwards", start=days_from_today(5), due=days_from_today(2))
    project.open_task("Backwards")
    expect(project.dialog.locator("#f-start")).to_have_value(days_from_today(2))
    expect(project.dialog.locator("#f-due")).to_have_value(days_from_today(5))


def test_move_task_to_another_project(project):
    project.quick_add("Wanderer")
    project.create_project("Other project")
    project.select_project("Test project")
    project.open_task("Wanderer")
    project.dialog.locator("#f-proj").select_option(label="Other project")
    project.save_task()
    expect(project.page.locator(".card")).to_have_count(0)
    project.select_project("Other project")
    assert project.titles_in("todo") == ["Wanderer"]


def test_task_title_is_shown_as_text_not_html(project):
    """Security check: a title containing HTML must never be run as HTML."""
    project.quick_add("<img src=x onerror=alert(1)>")
    expect(project.page.locator(".card img")).to_have_count(0)
    assert project.titles_in("todo") == ["<img src=x onerror=alert(1)>"]
