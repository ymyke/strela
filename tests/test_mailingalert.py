"""Test `MailingAlert`s."""

# pylint: disable=no-member,missing-function-docstring,protected-access
# pylint: disable=unused-argument,redefined-outer-name

import pytest
import yagmail
from tessa.price import PriceHistory
from strela.mailalert import MailingAlert, FinAlert
from strela.alertstates import FluctulertState
from .helpers import create_metric_history_df


# FIXME factor out common code for these tests (redundant w test_finalert, the next 3
# functions):
def dummy_callback(_: str) -> tuple:
    return (None, None)


def title_callback(ticker: str) -> str:
    return f"Alert title: {ticker}"


@pytest.fixture(autouse=True)
def patch_shelveloc(tmpdir):
    """Set temp directory for the FinAlert class so we don't override the production
    data.
    """
    # pylint: disable=protected-access
    saved_loc = FinAlert._FOLDER
    FinAlert._FOLDER = tmpdir
    yield
    FinAlert._FOLDER = saved_loc


def test_mailingalert_init():
    w = MailingAlert(
        alertname="x",
        metricname="y",
        tickers=["X"],
        alertstate_class=FluctulertState,
        get_metrichistory_callback=dummy_callback,
        alertstitle_callback=title_callback,
        to_email="y",
    )
    assert isinstance(w, MailingAlert)
    assert w.alertname == "x"
    assert w.metricname == "y"
    assert w.to_email == "y"
    assert w.tickers == ["X"]
    assert w.alertstate_class == FluctulertState
    # pylint: disable=comparison-with-callable
    assert w.get_metrichistory_callback == dummy_callback


def create_mailingalert(
    alertname: str = "TESTALERT",
    metricname: str = "TESTMETRIC",
    alertstate_class=FluctulertState,
):
    df = create_metric_history_df(allsame=False)
    df.iloc[-1]["close"] = 0
    return MailingAlert(
        alertname=alertname,
        metricname=metricname,
        tickers=["XXX"],
        alertstate_class=alertstate_class,
        get_metrichistory_callback=lambda _: PriceHistory(df=df, currency="any"),
        alertstitle_callback=title_callback,
        to_email="michael.naef@gmail.com",
    )


def test_mailingalert_mail_mocked(mocker):
    # FIXME If I ever refactor to using an adapter rather than a subclass in
    # mailalert.py, I could maybe test using a fake adapter and get rid the mocker here
    # and the entire pytest-mock import.
    mocker.patch("yagmail.SMTP")
    w = create_mailingalert()
    w.watch()
    yagmail.SMTP.assert_called_once_with("michael.naef@gmail.com")
    # FIXME ^ parametrize/make configurable
    yagmail.SMTP().send.assert_called_once_with(
        to="michael.naef@gmail.com",  # FIXME parametrize/make configurable
        subject="Fignal TESTMETRIC TESTALERT 📈🚨📉",
        contents=mocker.ANY,
    )
    assert "XXX" in str(yagmail.SMTP().send.call_args)
    assert "TESTMETRIC: 0" in str(yagmail.SMTP().send.call_args)

    # Run again and verify that nothing gets sent when there are no alerts:
    yagmail.SMTP.call_count = 0
    w.watch()
    yagmail.SMTP.assert_not_called()


# FIXME Have real email tests or remove the following two tests?

# @pytest.mark.enable_socket
# def test_mailingalert_mail_real():
#     create_mailingalert(alertname="Fluctulerts", metricname="Testprice").watch()


# @pytest.mark.enable_socket
# def test_mailingalert_mail_real_doubledown():
#     create_mailingalert(
#         alertname="Double Down Alerts",
#         metricname="Testprice",
#         alertstate_class=DoubleDownAlertState,
#     ).watch()
