from ldict.core.ldict_ import Ldict as ldict
from ldict.parameter.functionspace import FunctionSpace
from .appearance import decolorize
from .config import setup as setup
from .empty import Empty
from .parameter.let import Let as let

empty = Empty()
"""The empty object is used to induce a ldict from a dict"""

Ø = empty
"""UTF-8 alias for the empty object, it is used to induce a ldict from a dict. AltGr+Shift+o in most keyboards."""

decolorize = decolorize
