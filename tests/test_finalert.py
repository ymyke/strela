"""Test `FinAlert`s."""

# pylint: disable=missing-function-docstring

from dataclasses import dataclass
import re
import pytest
import pandas as pd
from strela.finalert import FinAlert, BasicCallbacks
from strela.alertstates import DoubleDownAlertState, FluctulertState
from .helpers import create_metric_history_df

# FIXME Opportunities to simplify this file and the tests in here?


@dataclass
class DummySymbol:
    name: str


@pytest.fixture(autouse=True)
def patch_shelveloc(tmpdir):
    """Set temp directory for the FinAlert class so we don't override the production
    data.
    """
    # pylint: disable=protected-access
    saved_loc = FinAlert._FOLDER
    FinAlert._FOLDER = tmpdir
    yield
    FinAlert._FOLDER = saved_loc


def test_init():
    a = FinAlert(
        [DummySymbol("X")],
        DoubleDownAlertState,
        "Alert",
        "N a*m/e",
        callbacks=BasicCallbacks,
    )
    assert isinstance(a, FinAlert)
    assert a.alertname == "Alert"
    assert a.metricname == "N a*m/e"
    assert a.alertstate_class == DoubleDownAlertState
    assert a.filename == "n-a-m-e-alert"
    assert a._fullpath.endswith("n-a-m-e-alert")  # pylint: disable=protected-access
    assert a.symbols == [DummySymbol("X")]
    assert a.callbacks == BasicCallbacks


def test_lookup_non_existing_ticker():  # FIXME Should be a repo test
    a = FinAlert(
        [DummySymbol("X")], DoubleDownAlertState, "x", "y", callbacks=BasicCallbacks
    )
    assert a.lookup_state("XXX") is None


def test_update_then_lookup_ticker():  # FIXME Should be a repo test
    a = FinAlert(
        [DummySymbol("X")], DoubleDownAlertState, "x", "y", callbacks=BasicCallbacks
    )
    assert a.lookup_state("XXX") is None
    a.update_state("XXX", "somethingtostore")
    assert a.lookup_state("XXX") == "somethingtostore"


@pytest.mark.parametrize(
    "df_changes, pattern",
    [
        (
            [],
            None,
        ),
        (
            [("2020-01-01", 1.01)],
            None,
        ),
        (
            [("2020-01-01", 100), ("2020-01-02", -100)],
            "↑↑↑ 101% · ↓↓↓ 99%",
        ),
        (
            [("2020-01-01", 100)],
            "↓↓↓ 99%",
        ),
        (
            [
                ("2020-01-01", 10),
                ("2020-01-02", -3),
                ("2020-05-19", 18),
            ],
            (
                "90d ·         · ↓↓↓ 94%\n180d ·         · ↓↓↓ 94%\n"
                "360d · ↑↑↑ 133% · ↓↓↓ 94%\nLatest Price: 1\n\n"
            ),
        ),
    ],
)
def test_generate_fluctulerts(df_changes, pattern):
    """The generate_alerts call produces correct Fluctulert alerts -- and no alerts if
    none are to be produced.
    """
    df = create_metric_history_df()
    for (timestamp, val) in df_changes:
        df.loc[timestamp, "close"] = val
    callbacks = BasicCallbacks()
    callbacks.metrichistory = lambda symbol: df
    alerts = FinAlert(
        [DummySymbol("EA")],
        FluctulertState,
        "Fluctulerts",
        "Price",
        callbacks=callbacks,
    ).generate_alerts()
    # FIXME Loads of setting up FinAlerts and PriceHistories in this file. Is there a
    # more elegant solution?
    if pattern:
        assert re.search(pattern, alerts, re.S)
    else:
        assert not alerts


def test_generate_alerts():
    """The generate_alerts call produces correct DoubleDown alerts -- and no alerts if
    none are to be produced.
    """
    df = create_metric_history_df()
    df.iloc[-1]["close"] = 0
    callbacks = BasicCallbacks()
    callbacks.metrichistory = lambda symbol: df
    alerts = FinAlert(
        [DummySymbol("X")],
        DoubleDownAlertState,
        "Double Down Alerts",
        "Price",
        callbacks=callbacks,
    ).generate_alerts()
    assert re.search("10×", alerts, re.S)


def test_generate_alerts_empty_history():
    callbacks = BasicCallbacks()
    callbacks.metrichistory = lambda symbol: pd.DataFrame()
    alerts = FinAlert(
        [DummySymbol("X")], DoubleDownAlertState, "x", "y", callbacks=callbacks
    ).generate_alerts()
    assert alerts is None


def test_shelf():
    """The shelf works as expected: I.e., no alert when no changes ocurred but do alert
    when changes did occur.
    """

    # Prepare price history df:
    df = pd.DataFrame(pd.date_range(start="01/01/2015", end="08/01/2020", tz="UTC"))
    df["close"] = 1
    df.set_index(0, inplace=True)
    df.loc["2020-08-01", "close"] = 0.7

    # First call of generate_alerts should create alert for EA:
    callbacks = BasicCallbacks()
    callbacks.metrichistory = lambda symbol: df
    finalert = FinAlert(
        [DummySymbol("EA")],
        DoubleDownAlertState,
        "Double Down Alerts",
        "Price",
        callbacks=callbacks,
    )
    alerts = finalert.generate_alerts()
    assert "EA" in alerts

    # Second call should not create an alert:
    alerts = finalert.generate_alerts()
    assert alerts is None

    # Third call, after changing the price history significantly, should produce an
    # alert again:
    df.loc["2020-07-31", "close"] = 0.7
    df.loc["2020-08-01", "close"] = 0.5
    finalert.callbacks.metrichistory = lambda symbol: df
    alerts = finalert.generate_alerts()
    assert "EA" in alerts
