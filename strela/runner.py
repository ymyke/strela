# FIXME Need something like this?
# FIXME Need a .bat script!?
# This module can also be called from the shell.

# - Shell invocation: python finalerts/alerts.py Fluctulerts P/E Or, if you want the
#   environment to be set up: C:\code\prod\fignal\utils\run_script.bat `
#     C:\code\prod\fignal\finalerts\alerts.py Fluctulerts Price
# - Code invocation: run("DDAlerts", "Price")

import datetime
from tessa.symbol import SymbolCollection, ExtendedSymbol
from strela.alert_generator import generate_alerts, AlertToStringTemplate, SymbolType
from strela.alertstates import (
    AlertStateRepository,
    AlertState,
    DoubleDownAlertState,
    FluctulertState,
)
from strela import mailer

# FIXME
# - Check for None alerts and then don't send any
# - What about the colors?

# FIXME Add to config?
NO_MAIL = False
FROM_EMAIL = "michael.naef@gmail.com"
TO_EMAIL = FROM_EMAIL


class AlertToHtmlTemplate(AlertToStringTemplate):
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


# FIXME
# - switch from string to list in generate alerts
# - "\n".join and "<br/>".join <- br necessary?


class MyAlertToHtmlTemplate(AlertToHtmlTemplate):
    def apply(self, symbol: SymbolType, *args, **kwargs) -> str:
        res = super().apply(symbol, *args, **kwargs).rstrip()
        try:
            # FIXME Add note re ExtendedSymbol and try etc...
            res += f"\nStrategy: {symbol.get_strategy_string()}\n"  # type: ignore
        except AttributeError:
            pass
        return res


# FIXME Have a templates.py with the basic_alert_string_generator and similar?

# Prepare the symbol lists:
sc = SymbolCollection(symbol_class=ExtendedSymbol)
sc.load_yaml("c:/code/fignal/mysymbols.yaml")  # FIXME Where to configure this?
crypto_symbols = [x for x in sc.symbols if x.watch and x.type_ == "crypto"]
stockx_symbols = [x for x in sc.symbols if x.watch and x.type_ != "crypto"]

# Blueprints for links to more information:
# # FIXME Could this be a tessa.symbol.Symbol concern?
COINGECKO_URL = "https://www.coingecko.com/en/coins/{symbol.name}"
GOOGLE_URL = "https://www.google.com/search?q={symbol.name}+stock"


# Set up the list of all the alert categories:
the_alert_list = [
    #
    # Every weekday: Check for double down alerts on both lists:
    #
    (
        stockx_symbols,  # Symbols to check
        "Stockx",  # Category name
        "DoubleDownAlert",  # Alert name
        DoubleDownAlertState,  # Alert state class
        range(0, 5),  # Weekdays to check
        GOOGLE_URL,  # Link pattern
    ),
    (
        crypto_symbols,
        "Crypto",
        "DoubleDownAlert",
        DoubleDownAlertState,
        range(0, 5),
        COINGECKO_URL,
    ),
    #
    # Every mon and thu: Check for fluctulerts on both lists:
    #
    (
        stockx_symbols,
        "Stockx",
        "Fluctulert",
        FluctulertState,
        [0, 3],
        GOOGLE_URL,
    ),
    (
        crypto_symbols,
        "Crypto",
        "Fluctulert",
        FluctulertState,
        [0, 3],
        COINGECKO_URL,
    ),
]

# Do the real work:
METRIC = "Price"
for (
    symbols,
    category_name,
    alert_name,
    alert_class,
    dayofweeks,
    link_pattern,
) in the_alert_list:
    if datetime.datetime.today().weekday() not in dayofweeks:
        continue
    template = MyAlertToHtmlTemplate(category_name, alert_name, METRIC, link_pattern)
    repo = AlertStateRepository(f"{category_name}-{METRIC}-{alert_name}")
    alerts = generate_alerts(
        alertstate_class=alert_class,
        metric_history_callback=lambda symbol: symbol.price_history().df,
        symbols=symbols,
        template=template,
        repo=repo,
    )
    if NO_MAIL:
        print(template.get_title() + "\n" + alerts)
    else:
        mailer.mail(
            from_=FROM_EMAIL,
            to_=TO_EMAIL,
            subject=template.get_title(),
            body=template.wrap_body(alerts),
        )
