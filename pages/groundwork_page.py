"""Page object for the Groundwork planner.

A page object wraps the screen in plain-English methods, so the tests read like
steps a person would take ("create a project", "start a task") and only this
file needs to change if the app's HTML changes.
"""
from pathlib import Path

from playwright.sync_api import Locator, Page

APP_URL = (Path(__file__).resolve().parent.parent / "app" / "index.html").as_uri()


class GroundworkPage:
    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.locator("dialog[open]")
        self.progress = page.locator(".strip-cap")
        self.heading = page.locator("main h1")
        self.search_box = page.locator("#search")
        self.priority_filter = page.get_by_label("Filter by priority")

    # ---- navigation -------------------------------------------------------
    def open(self) -> "GroundworkPage":
        self.page.goto(APP_URL)
        self.page.wait_for_selector("main h1")
        return self

    def reload(self) -> None:
        self.page.reload()
        self.page.wait_for_selector("main h1")

    def switch_view(self, name: str) -> None:
        """name is 'Board', 'List' or 'Timeline'."""
        self.page.locator(".tabs").get_by_role("button", name=name, exact=True).click()

    def active_view(self) -> str:
        return self.page.locator(".tabs button[aria-pressed='true']").inner_text()

    def select_project(self, name: str) -> None:
        self.page.locator("#plist").get_by_role("button", name=name).click()

    def sidebar_projects(self) -> list[str]:
        return self.page.locator("#plist .pname").all_inner_texts()

    # ---- projects ---------------------------------------------------------
    def create_project(self, name: str) -> None:
        self.page.locator("#newProject").click()
        self.dialog.locator("#f-pname").fill(name)
        self.dialog.get_by_role("button", name="Create project").click()

    def load_sample_project(self) -> None:
        self.page.get_by_role("button", name="Try a sample project").click()
        self.page.wait_for_selector(".card")

    def rename_project(self, new_name: str) -> None:
        self.page.get_by_role("button", name="Edit project").click()
        self.dialog.locator("#f-pname").fill(new_name)
        self.dialog.get_by_role("button", name="Save project").click()

    def delete_project(self, confirm: bool = True) -> None:
        self.page.get_by_role("button", name="Edit project").click()
        self.dialog.get_by_role("button", name="Delete project").click()
        if confirm:
            self.dialog.get_by_role("button", name="Confirm").click()

    # ---- tasks ------------------------------------------------------------
    def quick_add(self, title: str) -> None:
        box = self.page.get_by_label("New task title")
        box.fill(title)
        box.press("Enter")

    def add_task(self, title: str, *, status: str | None = None, priority: str | None = None,
                 start: str | None = None, due: str | None = None, notes: str | None = None,
                 steps: list[str] | None = None) -> None:
        """Add a task through the full dialog. Dates are 'YYYY-MM-DD'."""
        self.page.get_by_role("button", name="Add task").click()
        self._fill_task_form(title, status, priority, start, due, notes, steps)
        self.dialog.get_by_role("button", name="Save task").click()

    def open_task(self, title: str) -> None:
        self.page.locator(".card-t", has_text=title).first.click()
        self.dialog.wait_for()

    def save_task(self) -> None:
        self.dialog.get_by_role("button", name="Save task").click()

    def delete_open_task(self) -> None:
        self.dialog.get_by_role("button", name="Delete task").click()
        self.dialog.get_by_role("button", name="Confirm delete").click()

    def _fill_task_form(self, title, status, priority, start, due, notes, steps) -> None:
        self.dialog.locator("#f-title").fill(title)
        if status:
            self.dialog.locator(".seg label", has_text=status).click()
        if priority:
            self.dialog.locator("#f-prio").select_option(label=priority)
        if start:
            self.dialog.locator("#f-start").fill(start)
        if due:
            self.dialog.locator("#f-due").fill(due)
        if notes:
            self.dialog.locator("#f-notes").fill(notes)
        for step in steps or []:
            self.dialog.get_by_label("New checklist step").fill(step)
            self.dialog.get_by_role("button", name="Add step").click()

    # ---- board ------------------------------------------------------------
    def column(self, status: str) -> Locator:
        """status is 'todo', 'doing' or 'done'."""
        return self.page.locator(f".col[data-status='{status}']")

    def card(self, title: str) -> Locator:
        return self.page.locator(".card", has_text=title)

    def titles_in(self, status: str) -> list[str]:
        return self.column(status).locator(".card-t").all_inner_texts()

    def advance(self, title: str, action: str) -> None:
        """action is the button on the card: 'Start', 'Finish' or 'Reopen'."""
        self.card(title).get_by_role("button", name=action).click()

    def drag_to(self, title: str, status: str) -> None:
        self.card(title).drag_to(self.column(status))

    # ---- filters ----------------------------------------------------------
    def search(self, text: str) -> None:
        self.search_box.fill(text)

    def filter_priority(self, label: str) -> None:
        self.priority_filter.select_option(label=label)

    def visible_titles(self) -> list[str]:
        return self.page.locator("#body .card-t").all_inner_texts()
