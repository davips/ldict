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
import json
import operator
from functools import reduce
from random import Random
from typing import Dict, TypeVar, Union, Callable

from ldict.core.base import AbstractLazyDict
from ldict.core.rshift import handle_dict, lazify
from ldict.customjson import CustomJSONEncoder
from ldict.exception import WrongKeyType, ReadOnlyLdict
from ldict.lazyval import LazyVal
from ldict.parameter.functionspace import FunctionSpace
from ldict.parameter.let import AbstractLet

VT = TypeVar("VT")


class FrozenLazyDict(AbstractLazyDict):
    """Immutable lazy dict for serializable (picklable) pairs str->value

    Usage:

    >>> from ldict.frozenlazydict import FrozenLazyDict as ldict
    >>> ldict()
    {}
    >>> d = ldict(x=5, y=3)
    >>> d
    {
        "x": 5,
        "y": 3
    }
    >>> d["y"]
    3
    >>> ldict(x=123123, y=88)
    {
        "x": 123123,
        "y": 88
    }
    >>> ldict(y=88, x=123123)
    {
        "y": 88,
        "x": 123123
    }
    >>> d = ldict(x=123123, y=88)
    >>> e = d >> (lambda x: {"z": x**2}) >> (lambda x,y: {"w": x/y})
    >>> e
    {
        "x": 123123,
        "y": 88,
        "z": "→(x)",
        "w": "→(x y)"
    }
    >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x, y: {"w": x/y})
    >>> b = d >> (lambda x, y: {"w": x/y}) >> (lambda x: {"z": x**2})
    >>> dic = d.asdict  # Converting to dict
    >>> dic
    {'x': 123123, 'y': 88}
    >>> d2 = ldict(dic)  # Reconstructing from a dict
    >>> print(d2)
    {
        "x": 123123,
        "y": 88
    }
    >>> from ldict import empty
    >>> d = empty >> {"x": "more content"}
    >>> d
    {
        "x": "more content"
    }
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, rnd=None, _returned=None, **kwargs):
        self.rnd = rnd
        self.returned = _returned
        self.data = _dictionary or {}
        self.data.update(kwargs)

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise WrongKeyType(f"Key must be string, not {type(item)}.", item)
        if item not in self.data:
            raise KeyError(item)
        if isinstance(content := self.data[item], LazyVal):
            self.data[item] = content()
        return self.data[item]

    def __setitem__(self, key: str, value):
        del self[key]  # Reuse 'del' exception.

    def __delitem__(self, key):
        raise ReadOnlyLdict(f"Cannot change a frozen dict.", key)

    def __getattr__(self, item):
        if item in self:
            return self[item]
        return self.__getattribute__(item)

    def __repr__(self):
        txt = json.dumps(self.data, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
        return txt.replace('"«', "").replace('»"', "")

    __str__ = __repr__

    def evaluate(self):
        """
        >>> from ldict import ldict
        >>> f = lambda x: {"y": x+2}
        >>> d = ldict(x=3)
        >>> a = d >> f
        >>> a
        {
            "x": 3,
            "y": "→(x)"
        }
        >>> a.evaluate()
        >>> a
        {
            "x": 3,
            "y": 5
        }
        """
        for field in self:
            v = self[field]
            if isinstance(v, FrozenLazyDict):
                v.evaluate()

    @property
    def asdict(self):
        """
        >>> from ldict.frozenlazydict import FrozenLazyDict as ldict
        >>> d = ldict(x=3, y=5)
        >>> ldict(x=7, y=8, d=d).asdict
        {'x': 7, 'y': 8, 'd': {'x': 3, 'y': 5}}
        """
        dic = {}
        for field in self:
            v = self[field]
            dic[field] = v.asdict if isinstance(v, AbstractLazyDict) else v
        return dic

    def clone(self, data=None, rnd=None, _returned=None):
        """Same lazy content with (optional) new data or rnd object."""
        return FrozenLazyDict(self.data if data is None else data, rnd=rnd or self.rnd, _returned=_returned)

    def __rrshift__(self, left: Union[Random, Dict, Callable, FunctionSpace]):
        """
        >>> {"x":5} >> FrozenLazyDict()
        {
            "x": 5
        }
        >>> (lambda x:x*2) >> FrozenLazyDict()
        «λ × {}»
        >>> Random() >> FrozenLazyDict()
        {}
        """
        if isinstance(left, Random):
            return self.clone(rnd=left)
        if isinstance(left, Dict) and not isinstance(left, AbstractLazyDict):
            return FrozenLazyDict(left) >> self
        if callable(left):
            return FunctionSpace(left, self)
        return NotImplemented

    def __rshift__(self, other: Union[Dict, AbstractLazyDict, Callable, AbstractLet, FunctionSpace, Random]):
        from ldict import Empty

        if isinstance(other, Empty):
            return self
        if isinstance(other, Random):
            return self.clone(rnd=other)
        if isinstance(other, FrozenLazyDict):
            return self.clone(handle_dict(self.data, other, other.rnd), other.rnd)
        if isinstance(other, Dict):
            return self.clone(handle_dict(self.data, other, self.rnd))
        if isinstance(other, FunctionSpace):
            return reduce(operator.rshift, (self,) + other.functions)
        if callable(other) or isinstance(other, AbstractLet):
            lazies = lazify(self.data, output_field="extract", f=other, rnd=self.rnd, multi_output=True)
            data = self.data.copy()
            data.update(lazies)
            return self.clone(data, _returned=list(lazies.keys()))
        return NotImplemented

    def __eq__(self, other):
        if self.keys() != other.keys():
            return False
        self.evaluate()
        if isinstance(other, AbstractLazyDict):
            other.evaluate()
            return self.data == other.data
        if isinstance(other, Dict):
            return self.data == other
        raise TypeError(f"Cannot compare {type(self)} and {type(other)}")  # pragma: no cover
