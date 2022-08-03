import glob
import os
import shelve
import shutil
import time
from typing import Any, Optional, List, Callable, Type
from pandas import DataFrame
import slugify
from .alertstates import AlertState


class FinAlert:
    """Base class for all alert types.
    - Has a name, consisting of two parts: metric name and alert name
    - Knows the tickers.
    - Can save states (and writes backups).
    - Knows how to get the metric.
    - Returns alerts as a string

    Watches one metric and creates an alert if necessary. Handles state in order to only
    alert in case of changes. Returns alerts as a string.

    Additional attributes:
    - filename: Its filename for state information (without path information)
    - _fullpath: The full path including filename to store the shelf

    Main method:
    - watch
    """

    # FIXME Should this class be built around mixins rather than all that
    # parametrization that is necessary? -- Or group some of the arguments? E.g., a
    # group of callbacks? Not sure if that would be so much better though.

    _FOLDER = "./finalerts/data/"
    _BACKUPFOLDER = os.path.join(_FOLDER, "backups")

    def __init__(  # pylint: disable=too-many-arguments
        self,
        alertname: str,
        metricname: str,
        tickers: List[str],
        alertstate_class: Type[AlertState],
        get_metrichistory_callback: Callable[[str], DataFrame],
        alertstitle_callback: Callable[[str], str],
        comments_callback: Callable[[str], str] = None,
    ) -> None:
        """Args:
        - metricname: The name of the metric this alert is based on (e.g., "Price")
        - alertname: The name of the alert itself (e.g., "Fluctulert") (Note that the
          alertname and metricname are combined and used to derive the filename for the
          shelf. So make sure it is unique and consistent.)
        - tickers: The list of tickers to be watched.
        - alertstate_class: AlertState subclass to be used to track state and determine
          whether an alert has triggered
        - get_metrichistory_callback: Callback that returns historic data for that
          ticker and metric as a dataframe with timestamps as an index and one column
          with the metric
        - altertstitle_callback: Callback that takes a ticker and returns a string with
          this ticker's title in the alerts result string
        - comments_callback: Callback that takes a ticker and returns a string that will
          be displayed after an alert.
        """
        self.alertname = alertname
        self.metricname = metricname
        self.tickers = tickers
        self.alertstate_class = alertstate_class
        self.get_metrichistory_callback = get_metrichistory_callback
        self.alertstitle_callback = alertstitle_callback
        self.comments_callback = comments_callback
        self.filename = slugify.slugify(self.metricname + "-" + self.alertname)
        self._fullpath = os.path.join(self._FOLDER, self.filename)

    def lookup_ticker(self, ticker: str) -> Any:
        """Look up ticker's state in shelf. Return None if nothing is found."""
        try:
            with shelve.open(self._fullpath) as shelf:
                return shelf[ticker]
        except KeyError:
            return None

    def update_ticker(self, ticker: str, state: Any) -> None:
        """Update ticker's shelved state."""
        with shelve.open(self._fullpath, writeback=True) as shelf:
            shelf[ticker] = state

    def backup_shelf(self):
        """Move a copy of the shelf files to the backup folder."""
        for file in glob.glob(self._fullpath + "*"):
            shutil.copy(file, self._BACKUPFOLDER)

    def generate_alerts(self) -> Optional[str]:
        """Check list of tickers and return string with alerts, if any."""
        self.backup_shelf()
        alerts = ""
        for ticker in self.tickers:
            time.sleep(2)  # FIXME Is this necessary?
            # Get metric history:
            hist = self.get_metrichistory_callback(ticker).df
            if hist is None or not isinstance(hist, DataFrame) or hist.shape[0] == 0:
                continue
            latest = hist.values[-1][0]

            # Create the alertstate object:
            current_state = self.alertstate_class(hist)

            # Get the stored/old alertstate object:
            old_state = self.lookup_ticker(ticker)

            # Check if there was a change:
            if current_state.is_ringing() and not current_state.eq(old_state):
                self.update_ticker(ticker, current_state)
                alerts += self.alertstitle_callback(ticker) + "\n"
                alerts += f"{self.alertstate_to_string(current_state, old_state)}"
                alerts += f"Latest {self.metricname}: {latest}\n"
                if self.comments_callback is not None:
                    alerts += f"{self.comments_callback(ticker)}\n"
                alerts += "\n"
        return alerts or None

    def watch(self) -> None:
        """Check list of tickers and print alerts."""
        print(self.generate_alerts())

    @staticmethod
    def alertstate_to_string(state: AlertState, otherstate: AlertState) -> str:
        """Turn AlertState into string."""
        return state.stringify(otherstate)
