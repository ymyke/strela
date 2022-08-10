"""Main configuration file.

Configure the variables here to your needs. Since this file is under version control,
the best approach is to add your settings to a my_config.py file in the same directory
as this file. my_config.py will be imported at the end of this file and can thus be used
to overwrite settings in here.
"""

import os

# Debugging options:
# If True, ignore day-of-week settings and run on all days:
ENABLE_ALL_DOWS = False
# If True, don't send mail and instead print alerts to stdout:
NO_MAIL = False

MAIL_FROM_ADDRESS = "<your-email-address>"
MAIL_PASSWORD = "<please-use-application-password>"

# This is optional and only required if you load symbols from a file:
SYMBOLS_FILE = "<path-to-symbols-file>"

ALERT_REPOSITORY_FOLDER = "./data/"
assert os.path.isdir(
    ALERT_REPOSITORY_FOLDER
), f"{ALERT_REPOSITORY_FOLDER} doesn't exist, please create it."

# Try to load the overrides:
try:
    # pylint: disable=import-error,wildcard-import,unused-wildcard-import
    from .my_config import *  # type:ignore
except ImportError:
    pass

# Set some dynmamic variables:

MAIL_TO_ADDRESS = MAIL_FROM_ADDRESS
# This address will be used to send test mails to:
MAIL_TEST_TO_ADDRESS = MAIL_FROM_ADDRESS
