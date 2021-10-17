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
from functools import cached_property
from json import dumps
from random import Random
from typing import Dict

from ldict.core.base import AbstractLazyDict
from ldict.customjson import CustomJSONEncoder
from ldict.parameter.functionspace import FunctionSpace


class AbstractLet:
    def __init__(self, f, dict_type, **kwargs):
        self.f = f
        self.config = kwargs
        self.dict_type = dict_type

    @cached_property
    def asdict(self):
        return dumps(self.config, sort_keys=True, cls=CustomJSONEncoder)

    def __rshift__(self, other):
        if isinstance(other, dict):
            other = self.dict_type(other)
        if callable(other) or isinstance(other, (list, AbstractLazyDict)):
            return FunctionSpace(self, other)
        if isinstance(other, FunctionSpace):
            return FunctionSpace(self, *other.functions)
        return NotImplemented  # pragma: no cover

    def __rrshift__(self, other):
        if callable(other) or isinstance(other, (list, AbstractLazyDict, Random, AbstractLet)):
            return FunctionSpace(other, self)
        if isinstance(other, FunctionSpace):
            return FunctionSpace(*other.functions, self)
        if isinstance(other, Dict):
            return self.dict_type(other) >> self
        return NotImplemented  # pragma: no cover

    def __repr__(self):
        return "λ" + str(self.config)
