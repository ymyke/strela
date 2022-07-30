"""Test PeriodStat and FluctulertState classes."""

# pylint: disable=missing-function-docstring

import copy
import pandas as pd
import pytest
from strela.alertstates.fluctulertalertstate import FluctulertState, PeriodStat
from .helpers import create_metric_history_df

# ----- PeriodStat tests: -----


@pytest.mark.parametrize(
    "hdate, hclose, period, dtrigger, dmin, dmax",
    [
        ("2020-08-01", 1, 6, 0.1, 0, 0),
        ("2020-08-01", 2, 6, 0.1, 1.0, 0),
        ("2020-08-01", 2, 6, 0.6, 1.0, 0),
        ("2020-01-01", 2, 6, 0.1, 0, 0),
        ("2020-01-01", 2, 230, 0.1, 0, 0.5),
    ],
    ids=[
        "no canges",
        "dmin",
        "dmin regardless of trigger",
        "outside of period",
        "inside long period",
    ],
)
def test_periodstat_init(hdate, hclose, period, dtrigger, dmin, dmax):
    df = create_metric_history_df()
    df.loc[hdate, "close"] = hclose
    p = PeriodStat(period=period, dtrigger=dtrigger, hist=df)
    assert p.dmin == dmin
    assert p.dmax == dmax


def test_periodstat_empty_df():
    p = PeriodStat(period=1, dtrigger=0.5, hist=pd.DataFrame(columns=["a"]))
    assert p.dmin == 0 and p.dmax == 0


def test_periodstat_too_many_columns():
    with pytest.raises(ValueError):
        PeriodStat(period=1, dtrigger=0.5, hist=pd.DataFrame(columns=["a", "b"]))


def test_periodstat_eq_same():
    df = create_metric_history_df()
    ps1 = PeriodStat(period=100, dtrigger=0.1, hist=df)
    ps2 = PeriodStat(period=100, dtrigger=0.1, hist=df)
    assert ps1.eq(ps2)


def test_periodstat_eq_different():
    """Two PeriodStats differ if one of them triggers and the other doesn't."""
    df = create_metric_history_df()
    ps1 = PeriodStat(period=300, dtrigger=0.1, hist=df)
    df.loc["2020-01-01", "close"] = 100
    ps2 = PeriodStat(period=300, dtrigger=0.1, hist=df)
    assert not ps1.eq(ps2)


def test_periodstat_eq_smalldifference():
    """Two PeriodStats do not differ if the differences are too small to trigger."""
    df = create_metric_history_df()
    ps1 = PeriodStat(period=300, dtrigger=0.7, hist=df)
    df.loc["2020-01-01", "close"] = 2
    ps2 = PeriodStat(period=300, dtrigger=0.7, hist=df)
    assert ps1.eq(ps2)


# ----- FluctulertState tests: -----


@pytest.fixture(name="fs1")
def fixture_fs1():
    """Create FluctulertState object from df with all the same prices."""
    df = create_metric_history_df()
    yield FluctulertState(df)


@pytest.fixture(name="fs2")
def fixture_fs2():
    """Create FluctulertState with some variation."""
    df = create_metric_history_df()
    df.loc["2020-01-01", "close"] = 2
    df.loc["2020-03-01", "close"] = 4
    df.loc["2020-05-01", "close"] = 1.5
    df.loc["2020-07-30", "close"] = 0.5
    yield FluctulertState(df)


def test_fluctulertstate_init_allsame(fs1):
    assert len(fs1.stats) == 8
    assert sum(p.dmin for p in fs1.stats) == 0
    assert sum(p.dmax for p in fs1.stats) == 0
    # pylint: disable=protected-access
    assert sum(p.dtrigger for p in fs1.stats) == sum(
        t for _, t in FluctulertState._period_trigger_config
    )
    assert sum(p.period for p in fs1.stats) == sum(
        p for p, _ in FluctulertState._period_trigger_config
    )


def test_fluctulertstate_init_somedifferent(fs2):
    assert len(fs2.stats) == 8
    assert sum(p.dmin for p in fs2.stats) == 8
    assert sum(p.dmax for p in fs2.stats) == 1.5


def test_fluctulertstate_eq_same(fs1):
    otherps = copy.deepcopy(fs1)
    assert fs1.eq(otherps)


def test_fluctulertstate_eq_different(fs1, fs2):
    assert not fs1.eq(fs2)


def test_stringify(fs2):
    # pylint: disable=trailing-whitespace
    targetstring = """  3d · ↑↑↑ 100% ·        
  6d · ↑↑↑ 100% ·        
 14d · ↑↑↑ 100% ·        
 30d · ↑↑↑ 100% ·        
 60d · ↑↑↑ 100% ·        
 90d · ↑↑↑ 100% ·        
180d · ↑↑↑ 100% · ↓↓↓ 75%
360d · ↑↑↑ 100% · ↓↓↓ 75%
"""
    assert fs2.stringify() == targetstring
    # FIXME What if the format is configurable at some point in the future? E.g., with a
    # template.
