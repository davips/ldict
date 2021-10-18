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
from random import Random
from typing import Dict

from ldict.core.base import AbstractLazyDict


class AbstractFunctionSpace:
    def __init__(self, args, dict_type, empty_type):
        self.dict_type = dict_type
        self.empty_type = empty_type
        self.functions = args

    def __rshift__(self, other):
        if isinstance(other, self.empty_type):
            return self
        if isinstance(other, Dict) and not isinstance(other, AbstractLazyDict):
            other = self.dict_type(other)
        if callable(other) or isinstance(other, (AbstractLazyDict, AbstractFunctionSpace, list)):
            new_functions = other.functions if isinstance(other, AbstractFunctionSpace) else (other,)
            return self.__class__(*self.functions, *new_functions)
        return NotImplemented  # pragma: no cover

    __mul__ = __rshift__

    def __rrshift__(self, other):
        if isinstance(other, self.empty_type):
            return {} >> self
        if isinstance(other, Random):
            return self.__class__(other, *self.functions)
        if not isinstance(other, Dict) or isinstance(other, AbstractLazyDict):  # pragma: no cover
            return NotImplemented
        return reduce(operator.rshift, (self.dict_type(other),) + self.functions)

    def __repr__(self):
        txt = []
        for f in self.functions:
            if isinstance(f, list):
                s = "^"
            elif str(f).startswith("<function <lambda> at "):
                s = "λ"
            else:
                s = str(f)
            txt.append(s)
        return "«" + " × ".join(txt) + "»"
