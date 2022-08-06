"""Tests for the `AlertStateRepository` class"""

# pylint: disable=missing-function-docstring

import pytest
from strela.alertstates import AlertStateRepository, FluctulertState
from tests.helpers import create_metric_history_df


@pytest.fixture(autouse=True)
def patch_shelveloc(tmpdir):
    """Set temp directory for the repo so we don't override the production data."""
    # pylint: disable=protected-access
    saved_loc = AlertStateRepository._FOLDER
    AlertStateRepository._FOLDER = tmpdir
    yield
    AlertStateRepository._FOLDER = saved_loc


def test_init():
    repo = AlertStateRepository("t*e#s?t-TE ST")
    assert repo.filename == "t-e-s-t-te-st"
    assert repo._fullpath.endswith("t-e-s-t-te-st")  # pylint: disable=protected-access


def test_lookup_non_existing_symbol():
    repo = AlertStateRepository("reponame")
    assert repo.lookup_state("X") is None


def test_update_and_lookup_existing_symbol():
    repo = AlertStateRepository("reponame")
    assert repo.lookup_state("X") is None
    state = FluctulertState(create_metric_history_df())
    repo.update_state("X", state)
    assert state.eq(repo.lookup_state("X"))  # FIXME Type issue
