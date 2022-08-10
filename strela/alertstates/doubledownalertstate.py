from __future__ import annotations
from collections import namedtuple
from typing import Optional
import statistics
from pandas import DataFrame
from . import AlertState


class Level(namedtuple("Level", ["trigger", "factor"])):
    """Namedtuple subclass that overrides > operator to make things easier below."""

    def __gt__(self, other):
        return other is None or self.trigger > other.trigger


class DoubleDownAlertState(AlertState):
    """Concrete class for double-down alert states.

    Always keeps the current alert level including the date.

    Attributes:
    - currentlevel: The current alert level that is active. (Which does not necessarily
      mean that it has been activated just now. Check alertactivated for that.) None, if
      no level is active.
    - alertactivated: Records whether a new alert level has been reached by the latest
      history entry
    - alerthistory: History of all the alerts that have been triggered

    Settings / class attributes:
    - levels: The different levels at which alerts are triggered including the
      double-down factors for each level
    - averagingperiod: Number of days to average over when determining if an alert
      triggers.
    - cooldownperiod: After this number of days the alert resets to 0 if no new alert
      level has been reached.

    Note that -- due to the way this function is implemented -- days is not the same as
    dates. Days is more like trading days because there is usually no weekend data in
    the dataframes that are fed into the initiator.
    """

    # Class attributes:
    levels = [  # FIXME Should be configurable somewhere
        Level(trigger=0.1, factor=2),
        Level(trigger=0.2, factor=4),
        Level(trigger=0.3, factor=6),
        Level(trigger=0.4, factor=8),
        Level(trigger=0.5, factor=10),
    ]
    averagingperiod = 30
    cooldownperiod = 30

    def __init__(self, hist: DataFrame) -> None:
        super().__init__(hist)
        self.currentlevel = None
        self.alertactivated = False
        self.alerthistory = []
        self._scan_for_alerts(hist)

    def _scan_for_alerts(self, hist: DataFrame) -> Optional[Level]:
        """Scan the entire history hist for alerts and set up the corresponding
        attributes (alertactivated, alerthistory, currentlevel) in the object.
        """

        def _find_max_level(diff: int) -> Optional[Level]:
            """Return max level that gets triggered for diff. Or None if no level gets
            triggered.
            """
            for level in reversed(self.levels):
                if diff >= level.trigger:
                    return level
            return None

        dates = list(hist.index.values)
        values = list(hist.iloc[:, 0].values)
        origavg = None
        counter = None
        for i in range(self.averagingperiod, len(dates)):
            date, value = dates[i], values[i]
            self.alertactivated = False

            # (Re-)Set original average if no alert level active currently:
            if self.currentlevel is None:
                origavg = statistics.mean(values[i - self.averagingperiod : i])

            # Check if new alert level is reached:
            diff = (value - origavg) / origavg * -1
            newlevel = _find_max_level(diff)
            if newlevel and newlevel > self.currentlevel:
                self.alerthistory.append((date, newlevel))
                self.alertactivated = True
                self.currentlevel = newlevel
                counter = self.cooldownperiod

            # Cool down (if on an alert level currently):
            if self.currentlevel is not None:
                counter -= 1
                if counter == 0:
                    self.currentlevel = None

    def is_ringing(self) -> bool:
        return self.alertactivated

    def textify(self, other: Optional[DoubleDownAlertState] = None) -> str:
        if not self.currentlevel:
            return ""
        return (
            f"{self.currentlevel.trigger:.0%} down! "
            f"→ {self.currentlevel.factor}× invest!?\n"
        )

    def htmlify(self, other: Optional[DoubleDownAlertState] = None) -> str:
        return self.textify(other)

    def eq(self, other: Optional[DoubleDownAlertState]) -> bool:
        return other is not None and self.currentlevel == other.currentlevel
