from typing import Callable, Optional, List, Type
import pandas as pd
from strela.alertstates import AlertState, AlertStateRepository
from strela.symboltype import SymbolType
from strela.templates import AlertToStringTemplate


def generate_alerts(
    alertstate_class: Type[AlertState],
    metric_history_callback: Callable[[SymbolType], pd.DataFrame],
    symbols: List[SymbolType],
    template: AlertToStringTemplate,
    repo: AlertStateRepository,
) -> Optional[
    str
]:  # FIXME Switch to returning list of all alert strings, empty list if none.
    """Check list of symbols and return string with alerts. Returns `None` if no alerts
    are found.

    FIXME
    - metricname: The name of the metric this alert is based on (e.g., "Price")
    - alertname: The name of the alert itself (e.g., "Fluctulert") (Note that the
      alertname and metricname are combined and used to derive the filename for the
      shelf. So make sure it is unique and consistent.)
    - symbols: The list of symbols to be watched.
    - alertstate_class: AlertState subclass to be used to track state and determine
      whether an alert has triggered
    - get_metrichistory_callback: Callback that returns historic data for that symbol
      and metric as a dataframe with timestamps as an index and one column with the
      metric
    - altertstitle_callback: Callback that takes a symbol and returns a string with this
      symbol's title in the alerts result string
    - comments_callback: Callback that takes a symbol and returns a string that will be
      displayed after an alert.

    """
    repo.backup()  # FIXME Do this outside?
    alerts = ""
    for symbol in symbols:
        # Get metric history:
        hist = metric_history_callback(symbol)
        if hist is None or not isinstance(hist, pd.DataFrame) or hist.shape[0] == 0:
            continue
        latest_value = hist.values[-1][0]

        # Create the alertstate object:
        current_state = alertstate_class(hist)

        # Get the stored/old alertstate object:
        old_state = repo.lookup_state(symbol.name)

        # Check if there was a change:
        if current_state.is_ringing() and not current_state.eq(old_state):
            repo.update_state(symbol.name, current_state)
            alerts += template.apply(symbol, current_state, old_state, latest_value)
        # FIXME Type issues w old_state

    return alerts or None
