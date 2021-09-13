#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the ldict project.
#  Please respect the license - more about this in the section (*) below.
#
#  ldict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ldict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ldict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.
from dataclasses import dataclass
from typing import Dict

from ldict import Ldict, FunctionSpace


@dataclass
class Ldict_cfg:
    ldict: Ldict
    config: dict

    def __rshift__(self, other):
        return self.ldict.__rshift__(other, self.config)


class cfg:
    """
    Set values or sampling intervals for parameterized functions

    >>> from ldict import Ø, ldict
    >>> f = lambda x,y, a=[-1,-0.9,-0.8,...,1]: {"z": a*x + y}
    >>> FS = Ø >> cfg(a=0) >> f
    >>> print(FS)
    «cfg{'a': 0}»
    >>> d = ldict(x=5,y=7) >> FS
    >>> print(d)
    {
        "id": "n-F.3dYV-Yaxvl8ehv.49FaBoj59zERdiBP0bdKD",
        "ids": "32wgpnPTM3eodSTkBkG-yECea859zERdiBP0bdKD... +1 ...Rs_92162dea64a7462725cac7dcee71b67669f69",
        "z": "→(a x y)",
        "x": 5,
        "y": 7
    }
    """

    def __init__(self, _f=None, **kwargs):
        self.config = kwargs
        self.f = _f

    def __rshift__(self, other):
        return FunctionSpace(cfg(_f=other, **self.config))

    def __rrshift__(self, other):
        from ldict import Ldict, Empty
        if isinstance(other, Empty):
            return self
        if isinstance(other, Dict):
            return other >> self
        return Ldict(other) >> self
        # return NotImplemented

    def __repr__(self):
        return "cfg" + str(self.config)
