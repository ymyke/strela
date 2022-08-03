"""Test `FinAlert`s."""

# pylint: disable=missing-function-docstring

import re
import pytest
import pandas as pd
from tessa.price import PriceHistory
from strela.finalert import FinAlert
from strela.alertstates import DoubleDownAlertState, FluctulertState
from .helpers import create_metric_history_df

# FIXME Opportunities to simplify this file and the tests in here?


def dummy_callback(_: str) -> tuple:
    return (None, None)


def title_callback(ticker: str) -> str:
    return f"Alert title: {ticker}"


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
        "Alert",
        "N a*m/e",
        tickers=["X"],
        alertstate_class=DoubleDownAlertState,
        get_metrichistory_callback=dummy_callback,
        alertstitle_callback=title_callback,
    )
    assert isinstance(a, FinAlert)
    assert a.alertname == "Alert"
    assert a.metricname == "N a*m/e"
    assert callable(a.get_metrichistory_callback)
    assert a.alertstate_class == DoubleDownAlertState
    assert a.filename == "n-a-m-e-alert"
    assert a._fullpath.endswith("n-a-m-e-alert")    # pylint: disable=protected-access
    assert a.tickers == ["X"]


def test_lookup_non_existing_ticker():
    w = FinAlert(
        "x",
        "y",
        tickers=["X"],
        alertstate_class=DoubleDownAlertState,
        get_metrichistory_callback=dummy_callback,
        alertstitle_callback=title_callback,
    )
    assert w.lookup_ticker("XXX") is None


def test_update_then_lookup_ticker():
    w = FinAlert(
        "x",
        "y",
        tickers=["X"],
        alertstate_class=DoubleDownAlertState,
        get_metrichistory_callback=dummy_callback,
        alertstitle_callback=title_callback,
    )
    assert w.lookup_ticker("XXX") is None
    w.update_ticker("XXX", "somethingtostore")
    res = w.lookup_ticker("XXX")
    assert res == "somethingtostore"


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
def test_generate_fluctulerts(
    df_changes,
    pattern,
):
    """The generate_alerts call produces correct Fluctulert alerts -- and no alerts if
    none are to be produced.
    """
    df = create_metric_history_df()
    for (timestamp, val) in df_changes:
        df.loc[timestamp, "close"] = val
    alerts = FinAlert(
        alertname="Fluctulerts",
        metricname="Price",
        tickers=["EA"],
        alertstate_class=FluctulertState,
        get_metrichistory_callback=lambda _: PriceHistory(df=df, currency="any"),
        alertstitle_callback=title_callback,
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
    alerts = FinAlert(
        alertname="Double Down Alerts",
        metricname="Price",
        tickers=["X"],
        alertstate_class=DoubleDownAlertState,
        get_metrichistory_callback=lambda _: PriceHistory(df=df, currency="any"),
        alertstitle_callback=title_callback,
    ).generate_alerts()
    assert re.search("10×", alerts, re.S)


def test_generate_alerts_empty_history():
    alerts = FinAlert(
        alertname="x",
        metricname="y",
        tickers=["X"],
        alertstate_class=DoubleDownAlertState,
        get_metrichistory_callback=lambda _: PriceHistory(
            df=pd.DataFrame(), currency="any"
        ),
        alertstitle_callback=title_callback,
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
    w = FinAlert(
        alertname="Double Down Alerts",
        metricname="Price",
        tickers=["EA"],
        alertstate_class=DoubleDownAlertState,
        get_metrichistory_callback=lambda _: PriceHistory(df=df, currency="any"),
        alertstitle_callback=title_callback,
    )
    s = w.generate_alerts()
    assert "EA" in s

    # Second call should not create an alert:
    s = w.generate_alerts()
    assert s is None

    # Third call, after changing the price history significantly, should produce an
    # alert again:
    df.loc["2020-07-31", "close"] = 0.7
    df.loc["2020-08-01", "close"] = 0.5
    w.get_metrichistory_callback = lambda _: PriceHistory(df=df, currency="any")
    s = w.generate_alerts()
    assert "EA" in s
