from playwright.sync_api import expect

from tests.conftest import days_from_today


def test_list_view_has_a_row_per_task(sample):
    sample.switch_view("List")
    expect(sample.page.locator("tbody tr")).to_have_count(7)


def test_list_view_sorts_by_due_date_with_done_last(project):
    project.add_task("Later", due=days_from_today(9))
    project.add_task("Sooner", due=days_from_today(2))
    project.add_task("No date")
    project.add_task("Finished", status="Done", due=days_from_today(1))
    project.switch_view("List")
    assert project.visible_titles() == ["Sooner", "Later", "No date", "Finished"]


def test_list_checkbox_marks_a_task_done(project):
    project.quick_add("Tick me")
    project.switch_view("List")
    project.page.get_by_label("Done: Tick me").check()
    expect(project.progress).to_have_text("1 of 1 tasks done")
    project.switch_view("Board")
    assert project.titles_in("done") == ["Tick me"]


def test_timeline_draws_a_bar_per_dated_task(sample):
    sample.quick_add("Undated task")
    sample.switch_view("Timeline")
    expect(sample.page.locator(".tl-bar")).to_have_count(7)
    expect(sample.page.locator(".tl-today")).to_be_visible()
    expect(sample.page.locator("#body .hint")).to_contain_text("1 task has no due date")


def test_timeline_with_no_dates_explains_what_to_do(project):
    project.quick_add("Undated")
    project.switch_view("Timeline")
    expect(project.page.locator("#body .hint")).to_contain_text("Give a task a due date")


def test_search_narrows_the_board(sample):
    sample.search("hosting")
    assert sample.visible_titles() == ["Choose a hosting plan"]


def test_search_is_case_insensitive_and_checks_notes(project):
    project.add_task("Plain title", notes="remember the INVOICE")
    project.quick_add("Something else")
    project.search("invoice")
    assert project.visible_titles() == ["Plain title"]


def test_search_with_no_match_says_so(sample):
    sample.search("zzzz-nothing")
    expect(sample.page.locator(".card")).to_have_count(0)
    expect(sample.column("todo")).to_contain_text("Nothing matches here.")


def test_priority_filter(sample):
    sample.filter_priority("High priority")
    assert len(sample.visible_titles()) == 3
    sample.filter_priority("All priorities")
    assert len(sample.visible_titles()) == 7


def test_search_box_keeps_focus_while_typing(sample):
    sample.search_box.click()
    sample.page.keyboard.type("photos")
    expect(sample.search_box).to_be_focused()
    assert sample.visible_titles() == ["Take photos for the gallery"]
