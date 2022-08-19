"""
.. include:: ../README.md
"""

__version__ = "0.2.3"

from . import config
from . import alertstates
from . import templates
from .alert_generator import generate_alerts
from .mailer import mail
from . import my_runner
