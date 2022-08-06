import yagmail
from .finalert import FinAlert
from .alertstates import AlertState

# FIXME Rename file to mailingalert.py

class MailingAlert(FinAlert):
    """Send a mail instead of simply returning a string."""

    # FIXME Should this be an adapter rather than a subclass? E.g., an adapter for text
    # output and one for email. Then we'd have just the base class which would take an
    # adapter as a parameter in the initializer. The email adapter would take everything
    # it needs from the configuation.

    _FROM_EMAIL = "michael.naef@gmail.com"

    def __init__(self, to_email: str, *args, **kwargs) -> None:
        """Args:
        - to_email: Recipient mail address
        """
        super().__init__(*args, **kwargs)
        self.to_email = to_email

    @staticmethod
    def alertstate_to_string(state: AlertState, otherstate: AlertState) -> str:
        """Turn AlertState into html. Overrides base function."""
        return state.htmlify(otherstate)

    def watch(self) -> None:
        """Check symbols and send a mail with all the alerts. Overrides base method."""
        alerts = self.generate_alerts()
        if alerts is not None:
            alerts = (
                '<pre><font face="Consolas, Lucida Console, Fira Code, Courier New, '
                'Courier, monospace">' + alerts + "</font></pre>"
            )
            # FIXME Need userid and pwd here to set up SMTP w/ those parameters bc they
            # cannot be taken from the keyring -- make configurable
            yagmail.SMTP(self._FROM_EMAIL).send(
                to=self.to_email,
                subject=f"Fignal {self.metricname} {self.alertname} 📈🚨📉",
                contents=alerts,
            )
