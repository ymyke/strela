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


def generate_alerts(
    # FIXME Add alertname? Maybe combine which_alertstate and alertname to a tuple?
    # Maybe have a register of all possible alerts with their names and classes? -- Same
    # with metricname and metric callback?
    which_alertstate: Type[AlertState],
    metricname: str,
    symbols: List[SymbolType],
    metrichistory_callback: Callable[[SymbolType], pd.DataFrame],
    generate_alert_string: Callable,
    repo: AlertStateRepository,
) -> Optional[str]:
    """Check list of symbols and return string with alerts. Returns `None` if no alerts
    are found.
    """
    repo.backup()  # FIXME Do this outside?
    alerts = ""
    for symbol in symbols:
        # Get metric history:
        hist = metrichistory_callback(symbol)
        if hist is None or not isinstance(hist, pd.DataFrame) or hist.shape[0] == 0:
            continue
        latest_value = hist.values[-1][0]

        # Create the alertstate object:
        current_state = which_alertstate(hist)

        # Get the stored/old alertstate object:
        old_state = repo.lookup_state(symbol.name)

        # Check if there was a change:
        if current_state.is_ringing() and not current_state.eq(old_state):
            repo.update_state(symbol.name, current_state)

            alerts += generate_alert_string(
                symbol,
                current_state.stringify(old_state),
                current_state.htmlify(old_state),
                metricname,
                latest_value,
            )
        # FIXME Type issues w old_state

    return alerts or None


def basic_alert_string_generator(
    symbol: SymbolType,
    alertstate_as_text: str,
    _alertstate_as_html: str,
    metricname: str,
    latest_value: float,
) -> str:
    res = f"""{symbol.name} ⚠lert
{alertstate_as_text.rstrip()}
Latest {metricname}: {latest_value}

"""
    try:
        res += f"Strategy: {symbol.get_strategy_string()}\n"  # type: ignore
    except AttributeError:
        pass
    return res


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
