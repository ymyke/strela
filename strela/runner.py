import datetime
from tessa.symbol import SymbolCollection, ExtendedSymbol
from strela.alert_generator import generate_alerts, AlertToStringTemplate, SymbolType
from strela.alertstates import (
    AlertStateRepository,
    DoubleDownAlertState,
    FluctulertState,
)

# FIXME Add mailing functionality

# FIXME Add HTMLTemplate here
# Use the below code but delete that subclass.
class ExtendedStringTemplate(AlertToStringTemplate):
    def apply(self, symbol: SymbolType, *args, **kwargs) -> str:
        res = super().apply(symbol, *args, **kwargs).rstrip()
        try:
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
    template = ExtendedStringTemplate(  # FIXME Use HTML template
        category_name, alert_name, METRIC, link_pattern
    )
    repo = AlertStateRepository(f"{category_name}-{METRIC}-{alert_name}")
    alerts = generate_alerts(
        alertstate_class=alert_class,
        metric_history_callback=lambda symbol: symbol.price_history().df,
        symbols=symbols,
        template=template,
        repo=repo,
    )
    print(template.get_title())
    print()
    print(alerts)
