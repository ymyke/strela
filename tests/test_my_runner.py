"""Orchestration/integration tests"""

# pylint: disable=unused-import, no-member, missing-function-docstring, unused-argument

import pytest
import yagmail
from tessa.price import PriceHistory
from strela import config
import strela.my_runner as runner
from .alertstates.test_alertstaterepository import patch_shelveloc
from .helpers import create_metric_history_df


@pytest.fixture(name="prepare_environment")
def fixture_prepare_environment(tmp_path):
    # Prepare environment:
    file = tmp_path / "symbols.yaml"
    file.write_text(
        """\
testcryptosymbolname:
  type_: crypto
  query: bankless-defi-innovation-index
  strategy: [HoldForGrowth, HoldForDiversification]
  watch: True
  jurisdiction: unknown
"""
    )
    config.SYMBOLS_FILE = file
    config.ENABLE_ALL_DOWS = True
    config.MAIL_TO_ADDRESS = config.MAIL_TEST_TO_ADDRESS


def test_price_run(mocker, prepare_environment):
    mocker.patch(
        "tessa.symbol.Symbol.price_history",
        return_value=PriceHistory(create_metric_history_df(allsame=False), "USD"),
    )
    mocker.patch("yagmail.SMTP")

    # Run:
    runner.run()

    # Check:
    yagmail.SMTP.assert_called()  # type: ignore
    yagmail.SMTP().send.assert_any_call(
        to=config.MAIL_TEST_TO_ADDRESS,
        subject="📈🚨📉 Crypto Price Fluctulert",
        contents=mocker.ANY,
    )
    assert "testcryptosymbolname" in str(yagmail.SMTP().send.call_args)


@pytest.mark.net
def test_mailingalert_mail_real(prepare_environment):
    """This will send mail to user."""
    runner.run()
