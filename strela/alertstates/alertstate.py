"""AlertState ABC"""

from __future__ import annotations
from typing import Optional
from abc import ABC, abstractmethod
from pandas import DataFrame


class AlertState(ABC):
    """The abstract base class for all alert states. Alert states encapsulate the logic
    to determine whether an alert has triggered or not.
    """

    @abstractmethod
    def __init__(self, hist: DataFrame) -> None:
        """Constructor. Takes a history dataframe `hist`. The dataframe must have
        timestamps as the index and exactly one column with the metric.
        """

    @abstractmethod
    def textify(self, other: Optional[AlertState] = None) -> str:
        """Return state as a text. Highlight differences to `other` if not None. Returns
        an empty string if nothing happened that would trigger an alert.
        """

    @abstractmethod
    def htmlify(self, other: Optional[AlertState] = None) -> str:
        """Return state as html. Returns empty string if there are no alerts."""

    @abstractmethod
    def eq(self, other: Optional[AlertState]) -> bool:
        """Check for equality of this alert and `other`. Note that `other` can be None."""

    @abstractmethod
    def is_ringing(self) -> bool:
        """Return `True` if this alert has been triggered (meaning in the last
        period) and not cooled down yet.
        """

    def __str__(self) -> str:
        return self.textify()
