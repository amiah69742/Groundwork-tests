import pytest
from playwright.sync_api import expect

from tests.conftest import days_from_today


@pytest.mark.smoke
@pytest.mark.parametrize("path, lands_in", [
    (["Start"], "doing"),
    (["Start", "Finish"], "done"),
    (["Start", "Finish", "Reopen"], "todo"),
])
def test_card_buttons_walk_a_task_through_the_board(project, path, lands_in):
    project.quick_add("Traveller")
    for action in path:
        project.advance("Traveller", action)
    assert project.titles_in(lands_in) == ["Traveller"]


def test_drag_a_card_to_done(project):
    project.quick_add("Drag me")
    project.drag_to("Drag me", "done")
    assert project.titles_in("done") == ["Drag me"]
    assert project.titles_in("todo") == []


def test_progress_caption_counts_done_tasks(project):
    project.quick_add("One")
    project.quick_add("Two")
    expect(project.progress).to_have_text("0 of 2 tasks done")
    project.advance("One", "Start")
    project.advance("One", "Finish")
    expect(project.progress).to_have_text("1 of 2 tasks done")


def test_progress_strip_has_one_segment_per_task(sample):
    expect(sample.page.locator(".strip span")).to_have_count(7)
    expect(sample.page.locator(".strip .s-done")).to_have_count(2)


def test_past_due_task_is_flagged_overdue(project):
    project.add_task("Late one", due=days_from_today(-3))
    expect(project.card("Late one")).to_contain_text("3 days overdue")
    expect(project.progress).to_contain_text("1 overdue")


def test_finished_task_is_never_overdue(project):
    project.add_task("Late but done", status="Done", due=days_from_today(-3))
    expect(project.card("Late but done")).not_to_contain_text("overdue")
    expect(project.progress).not_to_contain_text("overdue")


def test_due_today_wording(project):
    project.add_task("Today", due=days_from_today(0))
    expect(project.card("Today")).to_contain_text("Due today")


def test_column_counts(sample):
    expect(sample.column("todo").locator(".n")).to_have_text("3")
    expect(sample.column("doing").locator(".n")).to_have_text("2")
    expect(sample.column("done").locator(".n")).to_have_text("2")
