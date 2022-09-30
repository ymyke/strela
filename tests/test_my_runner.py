"""Orchestration/integration tests"""

# pylint: disable=unused-import, no-member, missing-function-docstring, unused-argument

import pytest
import pandas as pd
import yagmail
from tessa.price import PriceHistory, price_history
from strela import config
import strela.my_runner as runner
from .helpers import create_metric_history_df

# patch_shelveloc is an "autouse" fixture that sets the temporary folder for the repo:
from .alertstates.test_alertstaterepository import patch_shelveloc


@pytest.fixture(name="prepare_environment")
def fixture_prepare_environment(mocker, tmp_path):
    mocker.patch(
        "tessa.symbol.Symbol.price_history",
        return_value=PriceHistory(create_metric_history_df(allsame=False), "USD"),
    )
    file = tmp_path / "symbols.yaml"
    file.write_text(
        """\
testcryptosymbolname:
  source: coingecko
  strategy: [HoldForGrowth, HoldForDiversification]
  watch: True
  jurisdiction: unknown
"""
    )
    config.SYMBOLS_FILE = file
    config.ENABLE_ALL_DOWS = True
    config.MAIL_TO_ADDRESS = config.MAIL_TEST_TO_ADDRESS


def test_price_run(mocker, prepare_environment):
    """This will mock yagmail and verify if a mail would have been sent."""
    mocker.patch("yagmail.SMTP")
    runner.run()
    yagmail.SMTP.assert_called()  # type: ignore
    yagmail.SMTP().send.assert_any_call(
        to=config.MAIL_TEST_TO_ADDRESS,
        subject="📈🚨📉 Crypto Price Fluctulert",
        contents=mocker.ANY,
    )
    assert "testcryptosymbolname" in str(yagmail.SMTP().send.call_args)


@pytest.mark.net
def test_mailingalert_mail_real(mocker, prepare_environment):
    """This will actually send an email to the user."""
    runner.run()


@pytest.mark.net
def test_tessa_integration():
    """Make sure we can access price information via tessa."""
    res = price_history("ethereum", source="coingecko")
    assert isinstance(res.df, pd.DataFrame)
    assert res.df.shape[0] > 0
