"""Test the alert generator."""

# pylint: disable=missing-function-docstring

from dataclasses import dataclass
import re
import pytest
import pandas as pd
from strela.alert_generator import generate_alerts, AlertToStringTemplate
from strela.alertstates import (
    FluctulertState,
    DoubleDownAlertState,
    MemoryAlertStateRepository,
)
from .helpers import create_metric_history_df


@dataclass
class DummySymbol:
    name: str


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
    """`generate_alerts` produces correct Fluctulert alerts -- and no alerts if none are
    to be produced.
    """
    df = create_metric_history_df()
    for (timestamp, val) in df_changes:
        df.loc[timestamp, "close"] = val
    alerts = generate_alerts(
        alertstate_class=FluctulertState,
        metric_history_callback=lambda symbol: df,
        symbols=[DummySymbol("EA")],
        template=AlertToStringTemplate("", "", "Price"),
        # FIXME Also test categoryname and alertname? Or better have specific tests for
        # the template.
        repo=MemoryAlertStateRepository("x"),
    )
    # ^ FIXME Have one common args dict to use in all tests and just overwrite the
    # attributes that need to be overwritten?
    if pattern:
        assert re.search(pattern, alerts, re.S)
    else:
        assert not alerts


def test_generate_doubledown_alerts():
    """`generate_alerts` produces correct DoubleDown alerts -- and no alerts if
    none are to be produced.
    """
    df = create_metric_history_df()
    df.iloc[-1]["close"] = 0
    alerts = generate_alerts(
        alertstate_class=DoubleDownAlertState,
        metric_history_callback=lambda symbol: df,
        symbols=[DummySymbol("X")],
        template=AlertToStringTemplate("", "", "Price"),
        repo=MemoryAlertStateRepository("x"),
    )
    assert re.search("10×", alerts, re.S)


def test_generate_no_alerts_when_history_empty():
    alerts = generate_alerts(
        alertstate_class=DoubleDownAlertState,
        metric_history_callback=lambda symbol: pd.DataFrame(),
        symbols=[DummySymbol("X")],
        template=AlertToStringTemplate("", "", "x"),
        repo=MemoryAlertStateRepository("x"),
    )
    assert alerts is None


def test_repository_triggered_alert_not_to_trigger_again():
    """The repo works as expected: I.e., no alert when no changes ocurred but do alert
    when changes did occur.
    """

    # Prepare price history df:
    df = pd.DataFrame(pd.date_range(start="01/01/2015", end="08/01/2020", tz="UTC"))
    df["close"] = 1
    df.set_index(0, inplace=True)
    df.loc["2020-08-01", "close"] = 0.7

    # Set up arguments for `generate_alerts`:
    args = dict(
        alertstate_class=DoubleDownAlertState,
        metric_history_callback=lambda symbol: df,
        symbols=[DummySymbol("EA")],
        template=AlertToStringTemplate("", "", "Price"),
        repo=MemoryAlertStateRepository("x"),
    )

    # First call of generate_alerts should create alert for EA:
    alerts = generate_alerts(**args)
    assert "EA" in alerts

    # Second call with the same setup should not create an alert:
    alerts = generate_alerts(**args)
    assert alerts is None

    # Third call, after changing the price history significantly, should produce an
    # alert again:
    df.loc["2020-07-31", "close"] = 0.7
    df.loc["2020-08-01", "close"] = 0.5
    args["metric_history_callback"] = lambda symbol: df
    alerts = generate_alerts(**args)
    assert "EA" in alerts
