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
from ldict.parameter.functionspace import FunctionSpace


class Let:
    """
    Set values or sampling intervals for parameterized functions

    >>> from ldict import Ø, ldict, let
    >>> f = lambda x,y, a=[-1,-0.9,-0.8,...,1]: {"z": a*x + y}
    >>> FS = Ø >> let(a=0) >> f
    >>> print(FS)
    «let{'a': 0} × <lambda>»
    >>> d = ldict(x=5,y=7) >> FS
    >>> d.show(colored=False)
    {
        "id": "pZ3mdp6e2Azn0trhPbBvX7A1i4Tgap2AOIEYH4nm",
        "ids": {
            "z": "Ia4OVykOD55fBiLj6y6QJQ6NNeGgap2AOIEYH4nm",
            "x": ".T_f0bb8da3062cc75365ae0446044f7b3270977",
            "y": "mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8"
        },
        "z": "→(a x y)",
        "x": 5,
        "y": 7
    }
    """

    def __init__(self, **kwargs):
        self.config = kwargs

    def __rshift__(self, other):
        from ldict.core.ldict_ import Ldict
        if isinstance(other, Ldict):
            config = self.config.copy()
            config.update(other.config)
            return other.clone(let=config)
        if isinstance(other, dict):
            return Ldict(other)
        if callable(other) or isinstance(other, list):
            return FunctionSpace(self, other)
        if isinstance(other, FunctionSpace):
            return FunctionSpace(self, *other.functions)
        return NotImplemented

    def __rrshift__(self, other):
        if callable(other) or isinstance(other, list):
            return FunctionSpace(other, self)
        if isinstance(other, FunctionSpace):
            return FunctionSpace(*other.functions, self)
        return self >> other

    def __repr__(self):
        return "let" + str(self.config)
