"""FIXME"""

from __future__ import annotations
from abc import ABC, abstractmethod
from pandas import DataFrame


class AlertState(ABC):
    """ABC for all alert state classes.

    FIXME Explain the purpose of AlterState some more. Also, what are periods as
    mentioned in `is_ringing`?.
    """

    @abstractmethod
    def __init__(self, hist: DataFrame) -> None:
        """Mandatory init method that takes a history dataframe."""

    @abstractmethod
    def textify(self, other: AlertState = None) -> str:
        """Return state as a text. Highlight differences to other if not None. Returns
        an empty string if nothing happened that would trigger an alert.
        """

    @abstractmethod
    def htmlify(self, other: AlertState = None) -> str:
        """Return state as html. Returns empty string if there are no alerts."""

    @abstractmethod
    def eq(self, other: AlertState) -> bool:
        """Check for equality of this alert and other."""

    @abstractmethod
    def is_ringing(self) -> bool:
        """Return True if this alert has been triggered just now (meaning in the last
        period).
        """

    def __str__(self) -> str:
        return self.textify()
