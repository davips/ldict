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
import operator
from functools import reduce
from typing import Dict


class FunctionSpace:
    def __init__(self, *args):
        self.functions = args

    def __rshift__(self, other):
        from ldict import Ldict
        from ldict import Empty
        if isinstance(other, Empty):
            return self
        if isinstance(other, Dict) and not isinstance(other, Ldict):
            other = Ldict(other)
        if callable(other) or isinstance(other, (Ldict, FunctionSpace, list)):
            new_functions = other.functions if isinstance(other, FunctionSpace) else (other,)
            return FunctionSpace(*self.functions, *new_functions)
        return NotImplemented

    __mul__ = __rshift__

    def __rrshift__(self, other):
        from ldict import Ldict
        if not isinstance(other, Dict) or isinstance(other, Ldict):
            return NotImplemented
        return reduce(operator.rshift, (Ldict(other),) + self.functions)

    def __repr__(self):
        txt = []
        for f in self.functions:
            txt.append("^" if isinstance(f, list) else f.__name__)
        return " × ".join(txt)
