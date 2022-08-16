"""Main configuration file.

Configure the variables here to your needs. Since this file is under version control,
this is considered a default configuration, which requires to find an additional
configuration file with the user's (your) specific settings. This user config file is
expected to be called `my_config.py` and to be placed in either of these locations:

1. At the path the environment variable `STRELA_CONFIG_FILE` is set to.
2. The current directory.
3. In ~/.strela/my_config.py

A typical/minimal my_config.py might look like this:

```python
MAIL_FROM_ADDRESS = "<your email address>"
MAIL_PASSWORD = "<your email application password>"
SYMBOLS_FILE = "/path/to/your/symbols.yaml"
ALERT_REPOSITORY_FOLDER = "/path/to/your/alerts-data-folder/"
```

You could, for example, put everything in a hidden folder in your home directory with
the following items:
- ~/.strela/ -- folder for strela-related files
- ~/.strela/my_config.py -- user config file (will be found automatically)
- ~/.strela/data/ -- folder for the alert repository

Use this to verify what gets set in the end:
>>> import strela.config
>>> strela.config.print_current_configuation()
"""

import runpy
import os

# ---------- Settings ----------

LIBRARY_NAME = "strela"

# Debugging options:
# If True, ignore day-of-week settings and run on all days:
ENABLE_ALL_DOWS = False
# If True, don't send mail and instead print alerts to stdout:
NO_MAIL = False

# This is optional and can be used as a convenience if you want to load symbols from a
# file:
SYMBOLS_FILE = None  # path to symbols file

# Mail settings:
MAIL_FROM_ADDRESS = None  # your email address
MAIL_PASSWORD = None  # your email password; please use an application password

# The folder where the alert repo is stored:
ALERT_REPOSITORY_FOLDER = None
# FIXME Not all future repos need a folder (e.g., a sql db).

# ---------- Load user's settings file ----------

# Load user's config file that will overwrite some settings (especially all mandatory
# settings):
USER_CONFIG_MODULE_PATH = None  # path to user's config file; shouldn't be None at end
USER_CONFIG_MODULE_NAME = "my_config.py"

# Check the three possible locations for the user's config file:
for _path_candidate in [
    os.getenv("STRELA_CONFIG_FILE"),
    os.path.join(os.path.expanduser("~"), "." + LIBRARY_NAME, USER_CONFIG_MODULE_NAME),
    os.path.join(os.getcwd(), USER_CONFIG_MODULE_NAME),
]:
    if _path_candidate is not None and os.path.isfile(_path_candidate):
        USER_CONFIG_MODULE_PATH = _path_candidate
        break
if USER_CONFIG_MODULE_PATH is None:
    raise RuntimeError(
        f"No config file found. Please create {USER_CONFIG_MODULE_NAME} in "
        "either the current directory, ~/.strela/, or in the path "
        "specified by the environment variable STRELA_CONFIG_FILE."
    )

# Load the module at that path and update/overwrite the globals in this module with
# whatever we find in there that looks like a strela setting:
def looks_like_strela_setting(key: str) -> bool:
    """Return True if the key looks like a strela setting, i.e., all uppercase and not
    starting with a `_`.
    """
    return key.isupper() and not key.startswith("_")


new_globals = runpy.run_path(USER_CONFIG_MODULE_PATH)
globals().update({k: v for k, v in new_globals.items() if looks_like_strela_setting(k)})

# Make sure all mandatory variables are set:
MANDATORY_PARAMS = ["ALERT_REPOSITORY_FOLDER"]
for _name in MANDATORY_PARAMS:
    if globals().get(_name, None) is None:
        raise ValueError(f"Mandatory setting {_name} is not set. Check configuration.")

# Make sure the ALERT_REPOSITORY_FOLDER exists:
if not os.path.isdir(ALERT_REPOSITORY_FOLDER):
    raise FileNotFoundError(
        f"Alert repository folder {ALERT_REPOSITORY_FOLDER} doesn't exist. "
        "Please create it and/or check your configuration."
    )

# ---------- Set some settings that depend on other settings ----------

# Who the mail is sent to:
MAIL_TO_ADDRESS = MAIL_FROM_ADDRESS
# This address will be used to send test mails to:
MAIL_TEST_TO_ADDRESS = MAIL_FROM_ADDRESS

# ---------- END // Functions ----------


def print_current_configuation():
    """Print all the variables from this file (and whatever has been set/overwritten in
    the user's config file).
    """
    for k, v in sorted(globals().items()):
        if looks_like_strela_setting(k):
            print(f"{k} = {v}")
