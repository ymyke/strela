"""Orchestrate all the building blocks to create and send alerts.

It is intended to be run from a cron job or similar service (e.g., Windows Task
Scheduler). FIXME Add more notes here once the FIXMEs below are resolved.

This file is customized for my requirements and environment. Use it as a blueprint to
build your own runner.
"""

# FIXME Rename to runner-ymyke.py or similar?
# FIXME Mention keyring and the options to set password.
# FIXME Use keyring for mail address?
# FIXME Need something like this?
# FIXME Need a .bat script!?
# This module can also be called from the shell.
# - Shell invocation: python finalerts/alerts.py Fluctulerts P/E Or, if you want the
#   environment to be set up: C:\code\prod\fignal\utils\run_script.bat `
#     C:\code\prod\fignal\finalerts\alerts.py Fluctulerts Price
# - Code invocation: run("DDAlerts", "Price")

import datetime
from tessa.symbol import SymbolCollection, ExtendedSymbol
from strela.alert_generator import generate_alerts
from strela.symboltype import SymbolType
from strela.templates import AlertToHtmlTemplate
from strela.alertstates import (
    AlertStateRepository,
    DoubleDownAlertState,
    FluctulertState,
)
from strela import mailer


# FIXME Add to config?
SYMBOLS_FILE = "c:/code/fignal/mysymbols.yaml"
NO_MAIL = False
ENABLE_ALL_DOWS = False
FROM_EMAIL = "michael.naef@gmail.com"  # FIXME Remove my mail address
TO_EMAIL = FROM_EMAIL

# Blueprints for links to more information:
# FIXME Could this be a tessa.symbol.Symbol concern?
COINGECKO_URL = "https://www.coingecko.com/en/coins/{symbol.name}"
GOOGLE_URL = "https://www.google.com/search?q={symbol.name}+stock"


# Customized template derived from default HTML template:
class MyAlertToHtmlTemplate(AlertToHtmlTemplate):
    """Subclass that adds strategy information to an alert. Requires symbol to be of
    type `tessa.symbol.ExtendedSymbol`."""

    def apply(self, symbol: SymbolType, *args, **kwargs) -> str:
        return (
            super().apply(symbol, *args, **kwargs).rstrip()
            + f"\nStrategy: {symbol.get_strategy_string()}\n"  # type: ignore
        )


def run() -> None:
    """Set up everything and run the alert generation."""

    # Prepare the symbol lists:
    scoll = SymbolCollection(symbol_class=ExtendedSymbol)
    scoll.load_yaml(SYMBOLS_FILE)
    crypto_symbols = [x for x in scoll.symbols if x.watch and x.type_ == "crypto"]
    stockx_symbols = [x for x in scoll.symbols if x.watch and x.type_ != "crypto"]

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

    # Do the actual work:
    metric = "Price"
    for (
        symbols,
        category_name,
        alert_name,
        alert_class,
        dayofweeks,
        link_pattern,
    ) in the_alert_list:
        if (
            datetime.datetime.today().weekday() not in dayofweeks
            and not ENABLE_ALL_DOWS
        ):
            continue
        template = MyAlertToHtmlTemplate(
            category_name, alert_name, metric, link_pattern
        )
        repo = AlertStateRepository(f"{category_name}-{metric}-{alert_name}")
        alerts = generate_alerts(
            alertstate_class=alert_class,
            metric_history_callback=lambda s: s.price_history().df,  # type: ignore
            symbols=symbols,
            template=template,
            repo=repo,
        )
        alerts_str = "\n".join(alerts)  # pylint: disable=invalid-name
        if NO_MAIL:
            print(template.get_title() + "\n" + alerts_str)
        elif alerts:
            mailer.mail(
                from_=FROM_EMAIL,
                to_=TO_EMAIL,
                subject=template.get_title(),
                body=template.wrap_body(alerts_str),
            )


if __name__ == "__main__":
    run()
