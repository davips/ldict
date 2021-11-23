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
from typing import Callable, Dict, Union

from ldict.core.base import AbstractLazyDict
from ldict.customjson import CustomJSONEncoder
from ldict.parameter.functionspace import FunctionSpace


class AbstractLet:
    def __init__(self, f, dict_type, **kwargs):
        self.f = f
        self.dict_type = dict_type
        self.config = kwargs

    @cached_property
    def asdict(self):
        return self.config

    def __rrshift__(self, left: Union[Dict, Callable, "AbstractLet"]):
        """
        >>> from ldict import empty
        >>> {"x": 5, "y": 7} >> (Random(0) >> (empty >> (lambda x:{"y": 0})))
        {
            "x": 5,
            "y": "→(x)"
        }
        """
        if isinstance(left, dict) and not isinstance(left, AbstractLazyDict):
            return self.dict_type(left) >> self
        if callable(left):
            # noinspection PyArgumentList
            return FunctionSpace(self.__class__(left), self)
        if isinstance(left, (Random, list)):
            return FunctionSpace(self.dict_type(), left, self)
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other: Union[Dict, Callable]):
        if callable(other) or isinstance(other, (list, Random, AbstractLet, Dict)):
            return FunctionSpace(self, other)
        return NotImplemented  # pragma: no cover

    __mul__ = __rshift__

    def __repr__(self):
        return "λ" + str(self.config)
