from typing import Optional
from strela.symboltype import SymbolType
from strela.alertstates import AlertState

# FIXME Add tests
# FIXME Add documentation


class AlertToTextTemplate:
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
        old_state: Optional[AlertState],
        latest_value: float,
    ) -> str:
        return f"""\
{symbol.name} ⚠lert
{alert_state.textify(old_state).rstrip()}
Latest {self.metric_name}: {latest_value}
{self.link_pattern.format(symbol=symbol)}
"""


class AlertToHtmlTemplate(AlertToTextTemplate):
    def apply(
        self,
        symbol: SymbolType,
        alert_state: AlertState,
        old_state: AlertState,
        latest_value: float,
    ) -> str:
        return f"""\
<a href="{self.link_pattern.format(symbol=symbol)}">{symbol.name} ⚠lert</a>
{alert_state.htmlify(old_state).rstrip()}
Latest {self.metric_name}: {latest_value}
"""

    def wrap_body(self, body: str) -> str:
        return f"""\
<pre><font face="Consolas, Lucida Console, Fira Code, Courier New, Courier, monospace">
{body}
</font></pre>
"""
