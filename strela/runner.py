import datetime
from tessa.symbol import SymbolCollection, ExtendedSymbol
from strela.alert_generator import generate_alerts, AlertToStringTemplate, SymbolType
from strela.alertstates import (
    AlertStateRepository,
    DoubleDownAlertState,
    FluctulertState,
)

# FIXME Add HTMLTemplate here
# Use the below code but delete that subclass.
class ExtendedStringTemplate(AlertToStringTemplate):
    def apply(self, symbol: SymbolType, *args, **kwargs) -> str:
        res = super().apply(symbol, *args, **kwargs).rstrip()
        try:
            res += f"Strategy: {symbol.get_strategy_string()}\n"  # type: ignore
        except AttributeError:
            pass
        return res


# FIXME Have a templates.py with the basic_alert_string_generator and similar?

# Prepare the symbol lists:
sc = SymbolCollection(symbol_class=ExtendedSymbol)
sc.load_yaml("c:/code/fignal/mysymbols.yaml")  # FIXME Where to configure this?
crypto_symbols = [x for x in sc.symbols if x.watch and x.type_ == "crypto"]
stockx_symbols = [x for x in sc.symbols if x.watch and x.type_ != "crypto"]

# Set up 2 categories of alert sets:
category_list = [
    (crypto_symbols, "Crypto", "https://www.coingecko.com/en/coins/{symbol.name}"),
    (stockx_symbols, "Stockx", "https://www.google.com/search?q={symbol.name}+stock"),
]

# ----- DoubleDownAlerts -----
# Every weekday: Check for double down alerts on both lists:
if datetime.datetime.today().weekday() in range(0, 5):
    for symbols, category_name, link_pattern in category_list:
        template = ExtendedStringTemplate(  # FIXME Use HTML template
            category_name, "DoubleDownAlert", "Price", link_pattern
        )
        repo = AlertStateRepository(f"{category_name}-price-ddalerts")
        alerts = generate_alerts(
            alertstate_class=DoubleDownAlertState,
            metric_history_callback=lambda symbol: symbol.price_history().df,
            symbols=symbols,
            template=template,
            repo=repo,
        )
        print(template.get_title())
        print()
        print(alerts)


# ----- Fluctulerts -----
# Every mon and thu: Check for fluctulerts on both lists:
if datetime.datetime.today().weekday() in [0, 3]:
    for symbols, category_name, link_pattern in category_list:
        template = ExtendedStringTemplate(  # FIXME Use HTML template
            category_name, "Fluctulert", "Price", link_pattern
        )
        repo = AlertStateRepository(f"{category_name}-price-fluctulerts")
        alerts = generate_alerts(
            alertstate_class=FluctulertState,
            metric_history_callback=lambda symbol: symbol.price_history().df,
            symbols=symbols,
            template=template,
            repo=repo,
        )
        print(template.get_title())
        print()
        print(alerts)
