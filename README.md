# Groundwork test suite

![tests](https://github.com/YOUR-USERNAME/groundwork-tests/actions/workflows/tests.yml/badge.svg)

Automated end-to-end tests for [Groundwork](app/index.html), a browser-based project planner.
The suite drives a real Chromium browser with Playwright and checks the app the way a user
would use it: creating projects, adding tasks, dragging cards, switching views, reloading the page.

46 tests, about 30 seconds to run, and they run on every push through GitHub Actions.

## What it covers

| Area | File | Examples |
| --- | --- | --- |
| Projects | `tests/test_projects.py` | create, rename, required name, two-step delete, delete removes tasks |
| Tasks | `tests/test_tasks.py` | quick add, full dialog, edit, cancel, delete, checklist, date swap, HTML in titles |
| Board | `tests/test_board.py` | Start/Finish/Reopen, drag and drop, progress count, overdue rules |
| Views and filters | `tests/test_views_and_filters.py` | list sorting, timeline bars, search, priority filter |
| Persistence and layout | `tests/test_persistence_and_layout.py` | reload keeps data, corrupt storage, phone width, no JS errors |

The full plan, including what is out of scope and why, is in [docs/test-plan.md](docs/test-plan.md).

## How it is built

- **Page Object Model.** `pages/groundwork_page.py` wraps the screen in methods like
  `create_project()` and `advance()`. Tests never touch CSS selectors directly, so a change
  to the app's HTML means fixing one file instead of 46 tests.
- **Fixtures for setup.** `tests/conftest.py` provides `app` (empty), `project` (one empty
  project) and `sample` (seven realistic tasks), so each test starts from a known state.
- **Isolated tests.** Every test gets a fresh browser context, so saved data never leaks
  from one test into another and tests can run in any order.
- **No sleeps.** Assertions use Playwright's `expect`, which waits for the condition and
  retries, instead of fixed delays that make suites slow and flaky.
- **Dates relative to today.** Overdue and due-date tests compute dates from the current
  day, so they don't start failing next month.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

pytest                 # everything
pytest -m smoke        # the 7 must-pass checks
pytest --headed        # watch the browser do it
pytest -k overdue      # only tests with "overdue" in the name
```

## Project layout

```
app/index.html                 the application under test
pages/groundwork_page.py       page object
tests/                         the tests, grouped by feature
docs/test-plan.md              scope, approach, risks
.github/workflows/tests.yml    CI: runs the suite on every push
```
