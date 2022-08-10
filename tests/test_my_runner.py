"""Orchestration/integration tests"""

# pylint: disable=unused-import, no-member, missing-function-docstring, unused-argument

import pytest
import yagmail
from tessa.price import PriceHistory
import strela.my_runner as runner
from .alertstates.test_alertstaterepository import patch_shelveloc
from .helpers import create_metric_history_df

# FIXME Rename according to name of runner in the end.

TEST_EMAIL = "983409832498348938@mailinator.com"
# FIXME Use user's mail address once we have proper config in place?


@pytest.fixture(name="prepare_environment")
def fixture_prepare_environment(tmp_path):
    # Prepare environment:
    file = tmp_path / "symbols.yaml"
    file.write_text(
        """\
gmi:
  type_: crypto
  query: bankless-defi-innovation-index
  strategy: [HoldForGrowth, HoldForDiversification]
  watch: True
  jurisdiction: unknown
"""
    )
    runner.SYMBOLS_FILE = file
    runner.ENABLE_ALL_DOWS = True
    runner.TO_EMAIL = TEST_EMAIL


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
        to=TEST_EMAIL,
        subject="📈🚨📉 Crypto Price Fluctulert",
        contents=mocker.ANY,
    )
    assert "gmi" in str(yagmail.SMTP().send.call_args)


@pytest.mark.net  # FIXME Register somewhere
def test_mailingalert_mail_real(prepare_environment):
    """Will send mail to `TEST_EMAIL` address at mailinator.com. You can verify the
    arrival of the mail there.
    """
    runner.run()
