"""
.. include:: ../README.md
"""

__version__ = "0.3.2"

from . import config
from . import alertstates
from . import templates
from .alert_generator import generate_alerts
from .mailer import mail
from . import my_runner
