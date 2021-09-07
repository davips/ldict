from ldict_modules.appearance import decolorize
from ldict_modules.ldict_ import Ldict

ldict = Ldict

empty = ldict(readonly=True)
"""The empty object is used to induce a ldict from a dict"""

ø = empty
"""UTF-8 alias for the empty object, it is used to induce a ldict from a dict. AltGr+O in most keyboards."""

decolorize = decolorize
