"""AlertStateRepository class"""

import glob
import shutil
from typing import Optional
import os
import shelve
import slugify
from . import AlertState


class AlertStateRepository:
    """Simple repository for `AlertState`s based on `shelve` package.

    Note that the repo does not ensure uniqueness of symbol names. Different symbols
    with the same name are mapped to the same repository entry. Could consider creating
    more unique names by concatenating more information to the symbol name in the
    future.
    """

    _FOLDER = "c:/code/strela/data/"  # FIXME Make configurable
    _BACKUPFOLDER = os.path.join(_FOLDER, "backups")

    def __init__(self, filename: str):
        # self.filename = slugify.slugify(self.metricname + "-" + self.alertname)
        self.filename = slugify.slugify(filename)
        self._fullpath = os.path.join(self._FOLDER, self.filename)

    def lookup_state(self, symbol_name: str) -> Optional[AlertState]:
        """Look up ticker's state in shelf. Return None if nothing is found."""
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
