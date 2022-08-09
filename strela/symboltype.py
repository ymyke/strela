"""SymbolType class"""

from typing import Protocol


class SymbolType(Protocol):
    """The minimal symbol interface alerts rely on. A symbol needs at least a name and
    all the information necessary so the callbacks can do their work.

    This class is introduced so you can use your own symbol class. But you can also
    simply use `tessa.symbol.Symbol` (or a subclass) where a `SymbolType` is expected.
    """

    name: str
