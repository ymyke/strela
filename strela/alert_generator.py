"""Central function to analyze symbols and create alerts."""

from typing import Callable, List, Type
import pandas as pd
from strela.alertstates import AlertState, BaseAlertStateRepository
from strela.symboltype import SymbolType
from strela.templates import AlertToTextTemplate


def generate_alerts(
    alertstate_class: Type[AlertState],
    metric_history_callback: Callable[[SymbolType], pd.DataFrame],
    symbols: List[SymbolType],
    template: AlertToTextTemplate,
    repo: BaseAlertStateRepository,
) -> list[str]:
    """Check list of symbols and return a list of alert strings. Returns empty list if
    no alerts are found.

    - `alertstate_class`: The `strela.alertstates.AlertState` subclass to be used to
      track state and determine whether an alert has been triggered.
    - `get_metrichistory_callback`: Callback that returns historic data for the given
      symbol and the metric under observation as a dataframe. The dataframe must have
      timestamps as the index and exactly one column with the metric.
    - `symbols`: The list of symbols to be analyzed.
    - `template`: The template to use to generate the alert text.
    - `repo`: The repository to use to retrieve and store the state of alerts.

    Note that this function is kept very generic so you can plug in your own building
    blocks.
    """
    repo.backup()
    alerts = []
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
            alerts.append(
                template.apply(symbol, current_state, old_state, latest_value)
            )

    return alerts
