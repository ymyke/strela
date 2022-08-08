import yagmail


def mail(from_: str, to_: str, subject: str, body: str) -> None:
    # FIXME Need userid and pwd here to set up SMTP w/ those parameters bc they
    # cannot be taken from the keyring -- make configurable
    args = dict(
        to=to_, subject=subject, contents=body
    )
    try:
        yagmail.SMTP(from_).send(**args)
    except:
        try:
            yagmail.SMTP(from_, "").send(**args)    # FIXME Need password
        except:
            raise RuntimeError("Cannot send mail.")

