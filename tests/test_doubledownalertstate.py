"""Test DoubleDownAlertState class"""

# pylint: disable=no-member,missing-function-docstring,protected-access
# pylint: disable=unused-argument,redefined-outer-name,too-many-lines

import json
import numpy as np
import pandas as pd
from strela.alertstates import AlertState, DoubleDownAlertState
from strela.alertstates.doubledownalertstate import Level

# FIXME Most (all?) of these tests will break if the DoubleDownAlertState.Levels are set
# up differently. Maybe set the Levels explicitly here?

# Set up two dataframes that will be used in the following tests:
with open("tests/input_data/iusc_sw_history_excerpt.json", "r", encoding="utf-8") as f:
    HISTORY_AS_JSON = json.load(f)
HIST_NOALERT = pd.DataFrame(HISTORY_AS_JSON)
HIST_NOALERT.index = pd.to_datetime(HIST_NOALERT.index, unit="ms")
HIST_WITHALERT = HIST_NOALERT[HIST_NOALERT.index <= "2020-03-12"]


def test_init_without_active_alert():
    a = DoubleDownAlertState(HIST_NOALERT)
    assert isinstance(a, AlertState)
    assert a.currentlevel is None
    assert not a.alertactivated
    assert not a.is_ringing()
    assert a.stringify() == "" == a.htmlify()
    assert a.alerthistory == [
        (
            np.datetime64("2020-02-28T00:00:00.000000000"),
            Level(trigger=0.1, factor=2),
        ),
        (
            np.datetime64("2020-03-12T00:00:00.000000000"),
            Level(trigger=0.2, factor=4),
        ),
        (
            np.datetime64("2020-03-23T00:00:00.000000000"),
            Level(trigger=0.3, factor=6),
        ),
    ]


def test_init_with_active_alert():
    a = DoubleDownAlertState(HIST_WITHALERT)
    assert a.alertactivated
    assert a.is_ringing()
    assert a.currentlevel == a.levels[1]
    assert a.stringify() == "20% down! → 4× invest!?\n" == a.htmlify()
    # FIXME I guess the an alert's output should be configurable?


def test_init_with_several_levels_at_once():
    df = pd.DataFrame(pd.date_range(start="01/01/2015", end="08/01/2020", tz="UTC"))
    df["close"] = 1
    df.set_index(0, inplace=True)
    df.iloc[-1]["close"] = 0
    a = DoubleDownAlertState(df)
    assert a.alertactivated
    assert a.is_ringing()
    assert a.currentlevel == a.levels[4]


def test_eq_and_not_eq():
    a = DoubleDownAlertState(HIST_NOALERT)
    b = DoubleDownAlertState(HIST_WITHALERT)
    assert a.eq(a)
    assert not a.eq(b)
