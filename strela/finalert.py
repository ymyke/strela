import glob
import os
import shelve
import shutil
from typing import Optional, List, Type, Protocol
from pandas import DataFrame
import slugify
from .alertstates import AlertState


class SymbolType(Protocol):
    """Symbol interface for the FinAlert class. A symbol needs at least a name and all
    the information necessary so the callbacks can do their work.

    You can use `tessa.symbol.Symbol` where a `SymbolType` is expected.
    """

    name: str  # FIXME Try renaming and check if we get type errors.


class BasicCallbacks:
    # pylint: disable=unused-argument
    @classmethod
    def metrichistory(cls, symbol: SymbolType) -> DataFrame:
        return DataFrame()

    @classmethod
    def alerttitle(cls, symbol) -> str:
        return f"{symbol.name} ⚠lert"

    @classmethod
    def comments(cls, symbol: SymbolType) -> str:
        return ""


class PriceCallbacks(BasicCallbacks):
    @classmethod
    def metrichistory(cls, symbol) -> DataFrame:
        return symbol.get_pricehistory().df  # type: ignore


class FinAlert:
    """Base class for all alert types.
    - Has a name, consisting of two parts: metric name and alert name
    - Knows the symbols.
    - Can save states (and writes backups).
    - Knows how to get the metric.
    - Returns alerts as a string

    Watches one metric and creates an alert if necessary. Handles state in order to only
    alert in case of changes. Returns alerts as a string.

    Main method:
    - watch
    """

    # FIXME Should this class be built around mixins rather than all that
    # parametrization that is necessary? -- Or group some of the arguments? E.g., a
    # group of callbacks? Not sure if that would be so much better though.

    _FOLDER = "c:/code/strela/data/"  # FIXME Make configurable
    _BACKUPFOLDER = os.path.join(_FOLDER, "backups")

    def __init__(
        self,
        symbols: List[SymbolType],  # FIXME Change name to symbol?
        alertstate_class: Type[AlertState],
        alertname: str,
        metricname: str = "Price",
        callbacks: Type[BasicCallbacks] = PriceCallbacks,
    ) -> None:
        """Args:
        - metricname: The name of the metric this alert is based on (e.g., "Price")
        - alertname: The name of the alert itself (e.g., "Fluctulert") (Note that the
          alertname and metricname are combined and used to derive the filename for the
          shelf. So make sure it is unique and consistent.)
        - symbols: The list of symbols to be watched.
        - alertstate_class: AlertState subclass to be used to track state and determine
          whether an alert has triggered
        - get_metrichistory_callback: Callback that returns historic data for that
          ticker and metric as a dataframe with timestamps as an index and one column
          with the metric
        - altertstitle_callback: Callback that takes a ticker and returns a string with
          this ticker's title in the alerts result string
        - comments_callback: Callback that takes a ticker and returns a string that will
          be displayed after an alert.

        Additional attributes:
        - filename: Its filename for state information (without path information)
        - _fullpath: The full path including filename to store the shelf
        """
        self.alertname = alertname
        self.metricname = metricname
        self.symbols = symbols
        self.alertstate_class = alertstate_class
        self.callbacks = callbacks
        self.filename = slugify.slugify(self.metricname + "-" + self.alertname)
        self._fullpath = os.path.join(self._FOLDER, self.filename)

    def lookup_state(self, symbol_name: str) -> Optional[AlertState]:
        """Look up ticker's state in shelf. Return None if nothing is found."""
        # FIXME Should this be an injected repository rather than a shelf?
        try:
            with shelve.open(self._fullpath) as shelf:
                return shelf[symbol_name]
        except KeyError:
            return None

    def update_state(self, symbol_name: str, state: AlertState) -> None:
        """Update symbol's shelved state.

        Note that this class does not ensure that all symbols have different names. If
        different symbols have the same name, they are mapped to the same repository
        entry.
        """
        with shelve.open(self._fullpath, writeback=True) as shelf:
            shelf[symbol_name] = state

    def backup_shelf(self):
        """Move a copy of the shelf files to the backup folder."""
        for file in glob.glob(self._fullpath + "*"):
            shutil.copy(file, self._BACKUPFOLDER)

    def generate_alerts(self) -> Optional[str]:
        """Check list of symbols and return string with alerts, if any."""
        self.backup_shelf()
        alerts = ""
        for symbol in self.symbols:
            # Get metric history:
            hist = self.callbacks.metrichistory(symbol)
            if hist is None or not isinstance(hist, DataFrame) or hist.shape[0] == 0:
                continue
            latest = hist.values[-1][0]

            # Create the alertstate object:
            current_state = self.alertstate_class(hist)

            # Get the stored/old alertstate object:
            old_state = self.lookup_state(symbol.name)

            # Check if there was a change:
            if current_state.is_ringing() and not current_state.eq(old_state):
                self.update_state(symbol.name, current_state)
                alerts += self.callbacks.alerttitle(symbol) + "\n"
                alerts += f"{self.alertstate_to_string(current_state, old_state)}"
                alerts += f"Latest {self.metricname}: {latest}\n"
                if self.callbacks.comments is not None:
                    alerts += self.callbacks.comments(symbol) + "\n"
                alerts += "\n"
        return alerts or None

    def watch(self) -> None:
        """Check list of symbols and print alerts."""
        print(self.generate_alerts())

    @staticmethod
    def alertstate_to_string(state: AlertState, otherstate: AlertState) -> str:
        """Turn AlertState into string."""
        return state.stringify(otherstate)
