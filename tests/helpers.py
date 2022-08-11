"""Common helpers that are used in more than one test."""

import pandas as pd


def create_metric_history_df(allsame: bool = True):
    df = pd.DataFrame(pd.date_range(start="01/01/2015", end="08/01/2020", tz="UTC"))
    df["close"] = 1
    df.set_index(0, inplace=True)
    if not allsame:
        df.loc["2020-01-01", "close"] = 100
    return df
