"""Fluctulert state."""

from __future__ import annotations
from typing import Optional, ClassVar
from dataclasses import InitVar, dataclass, field
import re
from pandas import DataFrame
import pandas
from . import AlertState


@dataclass
class PeriodStat:
    """Helper class to calculate the stats for a given period in the history."""

    period: int
    """The period length in days."""

    dtrigger: float
    """Required dmin / dmax to trigger an alert."""

    hist: InitVar[DataFrame]
    """Dataframe with daily values for the metric."""

    dmin: float = field(init=False)
    """Difference in % between lastvalue and min value in period. Derived attribute."""

    dmax: float = field(init=False)
    """Difference in % between lastvalue and max value in period. Derived attribute."""

    def __post_init__(self, hist: DataFrame):
        """Calculate dmin and dmax.

        (post-init bc this is a dataclass that has a default initiator.)

        - `hist`: A dataframe with timestamp as the index and exactly 1 column with the
          values for the metric. The function picks this one column to do the
          calculations.

        (Example dataframe: '{"price":{"1604275200000":33.32}}')
        """
        if hist.shape[1] != 1:
            raise ValueError("Need a dataframe with exactly 1 column.")

        if len(hist) == 0:
            self.dmin = self.dmax = 0
            return

        colname = hist.columns[0]
        lastvalue = hist[colname][-1]
        today = hist.index[-1]
        from_date = today - pandas.offsets.DateOffset(days=self.period)
        from_date = from_date.strftime("%Y-%m-%d")
        minvalue = hist[hist.index > from_date].min()[colname]
        maxvalue = hist[hist.index > from_date].max()[colname]
        self.dmin = abs((lastvalue - minvalue) / minvalue)
        self.dmax = abs((maxvalue - lastvalue) / maxvalue)

    def maxtriggers(self) -> bool:
        """Whether it triggers on max."""
        return self.dmax >= self.dtrigger

    def mintriggers(self) -> bool:
        """Whether it triggers on min."""
        return self.dmin >= self.dtrigger

    def eq(self, other: PeriodStat) -> bool:
        """Check for equality of this PeriodStat and `other`. Equality simply means that
        both objects trigger the same way.
        """
        return (self.maxtriggers(), self.mintriggers()) == (
            other.maxtriggers(),
            other.mintriggers(),
        )


class FluctulertState(AlertState):
    """Concrete class for fluctulert states."""

    # Class variables:

    period_trigger_config: ClassVar[list] = [
        (3, 0.05),  # FIXME Should these be configurable?
        (6, 0.07),
        (14, 0.1),
        (30, 0.15),
        (60, 0.2),
        (90, 0.25),
        (180, 0.3),
        (360, 0.35),
    ]
    """The different levels at which to trigger. E.g., (14, 0.1) means: If there is a
    10% change in 14 days, trigger an alert."""

    # Instance variables:

    stats: list
    """A collection of `PeriodStat` objects."""

    def __init__(self, hist: DataFrame) -> None:
        super().__init__(hist)
        self.stats = [
            PeriodStat(period, trigger, hist)
            for period, trigger in self.period_trigger_config
        ]

    def textify(self, other: Optional[FluctulertState] = None) -> str:
        """Return all stats as a text. Returns an empty string if there are no stats,
        i.e., if nothing happened that would trigger a trigger.
        """
        s = ""
        for ps in self.stats:
            s += f"{ps.period:3d}d · "
            periodalerts = []
            periodalerts.append(
                f"↑↑↑ {ps.dmin:3.0%}" if ps.mintriggers() else "       "
            )
            periodalerts.append(
                f"↓↓↓ {ps.dmax:3.0%}" if ps.maxtriggers() else "       "
            )
            # (Alerts can happen both ways in one period.)
            s += " · ".join(periodalerts)
            s += "\n"
        if not ("↑" in s or "↓" in s):
            return ""
        return s

    def htmlify(self, other: Optional[FluctulertState] = None) -> str:
        """Return stats as html. Returns empty string if there are no alerts."""
        html = self.textify(other)
        html = re.sub(r"(↑↑↑)", r'<font color="green">\1</font>', html)
        html = re.sub(r"(↓↓↓)", r'<font color="red">\1</font>', html)
        return html

    def is_ringing(self) -> bool:
        return self.textify() != ""

    def eq(self, other: Optional[FluctulertState]) -> bool:
        """Check for equality of this PeriodStat and `other`."""
        return other is not None and all(
            a.eq(b) for a, b in zip(self.stats, other.stats)
        )
