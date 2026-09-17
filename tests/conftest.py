from datetime import date, timedelta

import pytest

from pages.groundwork_page import GroundworkPage


@pytest.fixture
def app(page) -> GroundworkPage:
    """A freshly opened app with no saved data.

    pytest-playwright gives every test its own browser context, so localStorage
    starts empty and tests can't leak data into each other.
    """
    return GroundworkPage(page).open()


@pytest.fixture
def project(app) -> GroundworkPage:
    """The app with one empty project called 'Test project' already created."""
    app.create_project("Test project")
    return app


@pytest.fixture
def sample(app) -> GroundworkPage:
    """The app with the built-in sample project loaded (7 tasks, 2 done)."""
    app.load_sample_project()
    return app


def days_from_today(n: int) -> str:
    return (date.today() + timedelta(days=n)).isoformat()
