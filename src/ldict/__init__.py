from ldict.persistence import setcache
from .appearance import decolorize
from .empty import Empty
from .functionspace import FunctionSpace
from .ldict_ import Ldict

ldict = Ldict


empty = Empty()
"""The empty object is used to induce a ldict from a dict"""

ø = empty
"""UTF-8 alias for the empty object, it is used to induce a ldict from a dict. AltGr+O in most keyboards."""

decolorize = decolorize
