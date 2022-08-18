"""AlertState repository classes"""

import glob
import shutil
from typing import Optional
import os
import shelve
import slugify
from strela import config
from . import AlertState


class BaseAlertStateRepository:
    """Simple repository that resides just in memory. It's also the base class for other
    repository classes. (*Note: Should add a proper ABC base class here eventually.
    (FIXME)*)
    """

    def __init__(self, _):
        self.states = {}

    def lookup_state(self, symbol_name: str) -> Optional[AlertState]:
        """Look up symbol's state. Return None if nothing is found."""
        try:
            return self.states[symbol_name]
        except KeyError:
            return None

    def update_state(self, symbol_name: str, state: AlertState) -> None:
        """Update symbol's state."""
        self.states[symbol_name] = state

    def backup(self):
        """Backup repo. No-op for this type of repo."""


class AlertStateRepository(BaseAlertStateRepository):
    """Simple repository for `AlertState`s based on shelve package."""

    _FOLDER = config.ALERT_REPOSITORY_FOLDER
    _BACKUPFOLDER = os.path.join(_FOLDER, "backups")

    def __init__(self, filename: str):  # pylint: disable=super-init-not-called
        """Create a new repository. `filename` is the name of the shelf file to be
        used."""
        self.filename = slugify.slugify(filename)
        self._fullpath = os.path.join(self._FOLDER, self.filename)

    def lookup_state(self, symbol_name: str) -> Optional[AlertState]:
        try:
            with shelve.open(self._fullpath) as shelf:
                return shelf[symbol_name]
        except KeyError:
            return None

    def update_state(self, symbol_name: str, state: AlertState) -> None:
        with shelve.open(self._fullpath, writeback=True) as shelf:
            shelf[symbol_name] = state

    def backup(self):
        """Move a copy of the shelf files to the backup folder."""
        for file in glob.glob(self._fullpath + "*"):
            shutil.copy(file, self._BACKUPFOLDER)
