"""Simple adapter to yagmail."""

import yagmail

# pylint: disable=bare-except, raise-missing-from


def mail(from_: str, to_: str, subject: str, body: str) -> None:
    """Send an email."""

    args = dict(to=to_, subject=subject, contents=body)
    try:
        # Try with the mail address only; this will look for a password in the keyring:
        yagmail.SMTP(from_).send(**args)
    except:
        try:
            # If that failed, try with email address and password:
            yagmail.SMTP(from_, "").send(**args)  # FIXME Need password
        except:
            raise RuntimeError("Cannot send mail.")
