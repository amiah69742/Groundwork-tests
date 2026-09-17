# Test plan: Groundwork planner

## Purpose

Confirm that the core user journeys in Groundwork work in a real browser, and catch
regressions automatically when the app changes.

## In scope

| # | Area | What is checked | Priority |
| --- | --- | --- | --- |
| 1 | Projects | Create, rename, delete with confirmation, required and trimmed names, "All projects" view | High |
| 2 | Tasks | Quick add, add with details, edit, cancel, delete, checklist, moving between projects | High |
| 3 | Board | Status buttons, drag and drop, column counts, progress caption and strip | High |
| 4 | Due dates | "Due today", "Due tomorrow", overdue wording, finished tasks never overdue, reversed dates | High |
| 5 | Views | List sorting and checkbox, timeline bars, today marker, undated hint | Medium |
| 6 | Filters | Search by title and notes, case-insensitive, priority filter, no-match message, focus kept | Medium |
| 7 | Persistence | Data and chosen view survive reload, corrupt saved data handled | High |
| 8 | Robustness | HTML in titles shown as text, no JavaScript errors, no sideways scroll at 375px | Medium |

## Out of scope

- **Firefox and Safari.** The suite runs Chromium only to keep CI fast. pytest-playwright
  supports `--browser firefox --browser webkit`, so this is a configuration change, not new tests.
- **Visual appearance.** Colors, fonts and spacing are not asserted. Screenshot comparison
  would be the next step.
- **Touch drag and drop.** Phones use the Start/Finish buttons, which are covered.
- **Performance** with thousands of tasks.
- **Accessibility audit.** Labels are relied on by the tests (many locators use
  `get_by_role` and `get_by_label`), which gives some coverage, but no axe-core scan is run.

## Approach

- Black-box, end-to-end tests through the UI. The app has no API to test below the UI.
- Test design techniques used: equivalence partitioning (blank, padded and valid names),
  boundary values (due yesterday, today, tomorrow), state transition testing
  (To do → Doing → Done → To do, run as a parametrized test), and negative testing
  (corrupt storage, HTML injection, reversed dates).
- Each test sets up its own data through fixtures and runs in a fresh browser context.

## Entry and exit criteria

- **Entry:** the app loads and the smoke tests (`pytest -m smoke`) pass.
- **Exit:** all tests pass in CI on the main branch.

## Risks

| Risk | Mitigation |
| --- | --- |
| Date-based tests fail around midnight, when "today" changes mid-test | Dates are computed per test; a rerun clears it. Freezing the browser clock would remove it fully. |
| Drag and drop is the most timing-sensitive interaction | One focused drag test; the button path covers the same state changes. |
| Tests coupled to HTML structure | All selectors live in the page object. |
