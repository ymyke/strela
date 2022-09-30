"""Orchestrate all the building blocks to create and send alerts.

This script is customized for my requirements and environment. Use it as a blueprint to
build your own runner.

It is intended to be run from a cron job or similar service (e.g., Windows Task
Scheduler). The way this script is set up, you can simply run it once a day and it'll
only run the alerts that are supposed to run on a given weekday.

If you work with a virtual environment, use a Bash script or something like this
Powershell script to set up your virtual environment and run the script:

```powershell
cd <project-root>
. ./.venv/Scripts/Activate.ps1
python strela/my_runner.py
```
"""


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
from strela import config


# Blueprints for links to more information:
# FIXME Could this be a tessa.symbol.Symbol concern?
COINGECKO_URL = "https://www.coingecko.com/en/coins/{symbol.name}"
GOOGLE_URL = "https://www.google.com/search?q={symbol.name}+stock"


# Customized template derived from default HTML template:
class MyAlertToHtmlTemplate(AlertToHtmlTemplate):
    """Template subclass that adds strategy information to an alert. Requires symbol to
    be of type `tessa.symbol.ExtendedSymbol`."""

    def apply(self, symbol: SymbolType, *args, **kwargs) -> str:
        return (
            super().apply(symbol, *args, **kwargs).rstrip()
            + f"\nStrategy: {symbol.get_strategy_string()}\n"  # type: ignore
        )


def run() -> None:
    """Set up everything and run the alert generation."""

    # Prepare the symbol lists:
    scoll = SymbolCollection()
    scoll.load_yaml(config.SYMBOLS_FILE, which_class=ExtendedSymbol)
    crypto_symbols = [x for x in scoll.symbols if x.watch and x.source == "coingecko"]
    stockx_symbols = [x for x in scoll.symbols if x.watch and x.source != "coingecko"]

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
            and not config.ENABLE_ALL_DOWS
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
        if config.NO_MAIL:
            print(template.get_title() + "\n" + alerts_str)
        elif alerts:
            mailer.mail(
                to_address=config.MAIL_TO_ADDRESS,
                subject=template.get_title(),
                body=template.wrap_body(alerts_str),
            )


if __name__ == "__main__":
    run()
