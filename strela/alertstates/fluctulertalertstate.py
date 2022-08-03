from __future__ import annotations
from dataclasses import InitVar, dataclass, field
import re
from pandas import DataFrame
import pandas
from . import AlertState

# FIXME Rename file to fluctulertstate.py?

@dataclass
class PeriodStat:
    """
    Args:
    - period: in days
    - dtrigger: required dmin / dmax to trigger an alert
    - hist: DataFrame with daily values for the metric (e.g., in the case of price
      history, as provided by Asset.price_history)

    Derived attributes:
    - dmin, dmax: difference in % between lastvalue and min / max value in period
    """

    period: int
    dtrigger: float
    hist: InitVar[DataFrame]

    dmin: float = field(init=False)
    dmax: float = field(init=False)

    def __post_init__(self, hist):
        """Calc dmin and dmax.

        (post-init bc this is a dataclass that has a default initiator.)

        Args:
        - hist: A dataframe with timestamp as the index and exactly 1 column with the
          values for the metric. The function picks this one column to do the
          calculations.

        (Example dataframe: '{"p-e":{"1604275200000":33.32}}')
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

    def maxtriggers(self):
        """Whether it triggers on max."""
        return self.dmax >= self.dtrigger

    def mintriggers(self):
        """Whether it triggers on min."""
        return self.dmin >= self.dtrigger

    def eq(self, other: PeriodStat) -> bool:
        """Check for equality of this PeriodStat and other. Equality simply means that
        both objects trigger the same way.
        """
        return (self.maxtriggers(), self.mintriggers()) == (
            other.maxtriggers(),
            other.mintriggers(),
        )


class FluctulertState(AlertState):
    """Concrete class for fluctulert states.

    Attributes:
    - stats: A collection of PeriodStat objects.

    Settings / class attributes:
    - _period_trigger_config: The different levels at which to trigger. E.g., (14, 0.1)
      means: If there is a 10% change in 14 days, trigger an alert.
    """

    stats = []

    _period_trigger_config = [
        (3, 0.05),
        (6, 0.07),
        (14, 0.1),
        (30, 0.15),
        (60, 0.2),
        (90, 0.25),
        (180, 0.3),
        (360, 0.35),
    ]

    def __init__(self, hist: DataFrame) -> None:
        super().__init__(hist)
        self.stats = [
            PeriodStat(period, trigger, hist)
            for period, trigger in self._period_trigger_config
        ]

    def stringify(self, other: FluctulertState = None) -> str:
        """Return all stats as a string. Returns an empty string if there are no stats,
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

    def htmlify(self, other: FluctulertState = None) -> str:
        """Return stats as html. Returns empty string if there are no alerts."""
        html = self.stringify(other)
        html = re.sub(r"(↑↑↑)", r'<font color="green">\1</font>', html)
        html = re.sub(r"(↓↓↓)", r'<font color="red">\1</font>', html)
        return html

    def is_ringing(self) -> bool:
        return self.stringify() != ""

    def eq(self, other: FluctulertState) -> bool:
        """Check for equality of this PeriodStat and other."""
        return other is not None and all(
            a.eq(b) for a, b in zip(self.stats, other.stats)
        )
