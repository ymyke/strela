"""
.. include:: ../README.md
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("your-package-name")
except PackageNotFoundError:
    __version__ = "unknown"


from . import config
from . import alertstates
from . import templates
from .alert_generator import generate_alerts
from .mailer import mail
from . import my_runner
