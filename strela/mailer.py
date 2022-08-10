"""Simple adapter to yagmail."""

import yagmail
from strela import config


def mail(to_address: str, subject: str, body: str) -> None:
    """Send an email. Note that the from-address is hardcoded and taken from the
    config.
    """
    try:
        yagmail.SMTP(config.MAIL_FROM_ADDRESS, config.MAIL_PASSWORD).send(
            to=to_address, subject=subject, contents=body
        )
    except Exception as exc:
        raise RuntimeError("Cannot send mail.") from exc
