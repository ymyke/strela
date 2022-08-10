"""AlertStateRepository class"""

import glob
import shutil
from typing import Optional
import os
import shelve
import slugify
from strela import config
from . import AlertState


class AlertStateRepository:
    """Simple repository for `AlertState`s based on `shelve` package.

    Note that the repo does not ensure uniqueness of symbol names. Different symbols
    with the same name are mapped to the same repository entry. Could consider creating
    more unique names by concatenating more information to the symbol name in the
    future.
    """

    _FOLDER = config.ALERT_REPOSITORY_FOLDER
    _BACKUPFOLDER = os.path.join(_FOLDER, "backups")

    def __init__(self, filename: str):
        self.filename = slugify.slugify(filename)
        self._fullpath = os.path.join(self._FOLDER, self.filename)

    def lookup_state(self, symbol_name: str) -> Optional[AlertState]:
        """Look up symbol's state in shelf. Return None if nothing is found."""
        try:
            with shelve.open(self._fullpath) as shelf:
                return shelf[symbol_name]
        except KeyError:
            return None

    def update_state(self, symbol_name: str, state: AlertState) -> None:
        """Update symbol's shelved state."""
        with shelve.open(self._fullpath, writeback=True) as shelf:
            shelf[symbol_name] = state

    def backup(self):
        """Move a copy of the shelf files to the backup folder."""
        for file in glob.glob(self._fullpath + "*"):
            shutil.copy(file, self._BACKUPFOLDER)

# FIXME Reverse the class hierarchy? Then the MemoryAlertStateRepository would not use
# the filename attribute?

class MemoryAlertStateRepository(AlertStateRepository):
    """AlertStateRepository that is simply in memory."""

    def __init__(self, _): # pylint: disable=super-init-not-called
        self.states = {}

    def lookup_state(self, symbol_name: str) -> Optional[AlertState]:
        try:
            return self.states[symbol_name]
        except KeyError:
            return None

    def update_state(self, symbol_name: str, state: AlertState) -> None:
        self.states[symbol_name] = state

    def backup(self):
        pass
