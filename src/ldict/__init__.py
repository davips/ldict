from .appearance import decolorize
from .config import setup as setup
from .core.ldict_ import Ldict as ldict
from .empty import Empty
from .parameter.functionspace import FunctionSpace
from .parameter.let import Let as let

empty = Empty()
"""The empty object is used to induce a ldict from a dict"""

Ø = empty
"""UTF-8 alias for the empty object, it is used to induce a ldict from a dict. AltGr+Shift+o in most keyboards."""

decolorize = decolorize
