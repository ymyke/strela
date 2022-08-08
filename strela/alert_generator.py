from typing import Callable, Optional, Protocol, List, Type
import pandas as pd
from strela.alertstates.alertstaterepository import AlertStateRepository
from strela.alertstates import AlertState


class SymbolType(Protocol):
    """Symbol interface for the FinAlert class. A symbol needs at least a name and all
    the information necessary so the callbacks can do their work.

    You can use `tessa.symbol.Symbol` where a `SymbolType` is expected.
    """

    name: str


class AlertToStringTemplate:
    def __init__(
        self,
        category_name: str,
        alert_name: str,
        metric_name: str,
        link_pattern: str = "",
    ):
        self.category_name = category_name
        self.alert_name = alert_name
        self.metric_name = metric_name
        self.link_pattern = link_pattern
        # e.g. "https://www.google.com/search?q={symbol.name}+stock" FIXME add to doc

    def get_title(self) -> str:
        return f"📈🚨📉 {self.category_name} {self.metric_name} {self.alert_name}"

    def apply(
        self,
        symbol: SymbolType,
        alert_state: AlertState,
        old_state: AlertState,
        latest_value: float,
    ) -> str:
        return f"""{symbol.name} ⚠lert
{alert_state.stringify(old_state).rstrip()}
Latest {self.metric_name}: {latest_value}
{self.link_pattern.format(symbol=symbol)}

"""


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


# FIXME How would this integrate with the mailing alert?

# FIXME What to do with this?
# # Set the title callback:
# if tickerlistname == "Cryptotickers":
#     alertstitle_callback = lambda ticker: (
#         f'<a href="https://www.coingecko.com/en/coins/'
#         f'{api.coingecko.symbol_to_id(ticker)}">'
#         f"{ticker} ⚠lert</a>"
#     )
# else:
#     alertstitle_callback = lambda ticker: (
#         f'<a href="https://www.google.com/search?q='
#         f'{ticker}+stock">{ticker} ⚠lert</a>'
#     )
