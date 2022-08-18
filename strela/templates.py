"""Templates that turn alerts into strings.

- Currently, alerts are already barebone strings, and these templates rather "embellish"
  them.
- There are no specific tests for this module bc other tests also implicitly test the
  templates.
"""

from typing import Optional
from strela.symboltype import SymbolType
from strela.alertstates import AlertState


class AlertToTextTemplate:
    """Template to turn alert into text string. Also serves as the base class for other
    templates. (*Note: Should add a proper ABC for templates rather than using
    AlertToTextTemplate (FIXME).*)
    """

    def __init__(
        self,
        category_name: str,
        alert_name: str,
        metric_name: str,
        link_pattern: str = "",
    ):
        """`AlertToTextTemplate` initializer.

        - `category_name`: Alert category, e.g. "Crypto".
        - `alert_name`: Alert name, e.g. "Fluctulert".
        - `metric_name`: Metric name, e.g. "Price".
        - `link_pattern`: Link pattern, will be extrapolated in `apply`, e.g.
          "https://www.google.com/search?q={symbol.name}+stock"

        All the names are informational only and have no functional purpose.
        """
        self.category_name = category_name
        self.alert_name = alert_name
        self.metric_name = metric_name
        self.link_pattern = link_pattern

    def get_title(self) -> str:
        """Return the title/subject of the alert."""
        return f"📈🚨📉 {self.category_name} {self.metric_name} {self.alert_name}"

    def apply(
        self,
        symbol: SymbolType,
        alert_state: AlertState,
        old_state: Optional[AlertState],
        latest_value: float,
    ) -> str:
        """Extrapolate the template into a string and return it.

        - `symbol`: Symbol for which the alert is being generated.
        - `alert_state`: Current state of the alert.
        - `old_state`: Previous state of the alert.
        - `latest_value`: Latest value of the metric.
        """
        return f"""\
{symbol.name} ⚠lert
{alert_state.textify(old_state).rstrip()}
Latest {self.metric_name}: {latest_value}
{self.link_pattern.format(symbol=symbol)}
"""


class AlertToHtmlTemplate(AlertToTextTemplate):
    """Template subclass that generates HTML."""

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
        """Wrap the alert in HTML wrapper tags."""
        return f"""\
<pre><font face="Consolas, Lucida Console, Fira Code, Courier New, Courier, monospace">
{body}
</font></pre>
"""
