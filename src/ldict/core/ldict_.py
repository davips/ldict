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
import operator
from functools import reduce
from random import Random
from typing import Dict, TypeVar, Union, Callable

from ldict.core.base import AbstractLazyDict
from ldict.core.rshift import handle_dict, lazify
from ldict.exception import WrongKeyType
from ldict.frozenlazydict import FrozenLazyDict
from ldict.parameter.functionspace import FunctionSpace
from ldict.parameter.let import Let

VT = TypeVar("VT")


class Ldict(AbstractLazyDict):
    """Mutable lazy dict for serializable (picklable) pairs str->value

    Usage:

    >>> from ldict import ldict
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
    >>> from ldict import Ø
    >>> d = Ø >> {"x": "more content"}
    >>> d
    {
        "x": "more content"
    }
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, rnd=None, **kwargs):
        self.rnd = rnd
        self.frozen = FrozenLazyDict(_dictionary or kwargs, rnd=rnd)

    def __getitem__(self, item):
        return self.frozen[item]

    def __setitem__(self, key: str, value):
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        self.frozen >>= {key: value}

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        data = self.frozen.data.copy()
        del data[key]
        return self.frozen.clone(data)

    def __getattr__(self, item):
        return self.frozen[item]

    def __repr__(self):
        return repr(self.frozen)

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
        self.frozen.evaluate()

    @property
    def asdict(self):
        """
        >>> from ldict import ldict
        >>> d = ldict(x=3, y=5)
        >>> ldict(x=7, y=8, d=d).asdict
        {'x': 7, 'y': 8, 'd': {'x': 3, 'y': 5}}
        """
        return self.frozen.asdict

    def clone(self, data=None, rnd=None):
        """Same lazy content with (optional) new data or rnd object."""
        return Ldict(self.frozen.data if data is None else data, rnd=rnd or self.rnd)

    def __rrshift__(self, other: Union[Dict, Callable, FunctionSpace]):
        if isinstance(other, Dict):
            return Ldict(other) >> self
        if callable(other):
            return FunctionSpace(other, self)
        return NotImplemented

    def __rshift__(self, other: Union[Dict, 'Ldict', Callable, Let, FunctionSpace, Random]):
        from ldict import Empty
        if isinstance(other, Random):
            return self.clone(rnd=other)
        if isinstance(other, Empty):
            return self
        if isinstance(other, Ldict):
            return self.clone(handle_dict(self.frozen.data, other, other.rnd), other.rnd)
        if isinstance(other, Dict):
            return self.clone(handle_dict(self.frozen.data, other, self.rnd))
        if isinstance(other, FunctionSpace):
            return reduce(operator.rshift, (self,) + other.functions)
        if callable(other) or isinstance(other, Let):
            lazies = lazify(self.frozen.data, output_field="extract", f=other, rnd=self.rnd, multi_output=True)
            data = self.frozen.data.copy()
            data.update(lazies)
            return self.clone(data)
        raise NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        # REMINDER: idict and cdict should compared ids
        if isinstance(other, FrozenLazyDict):
            self.evaluate()
            other.evaluate()
            return self.data == other.data
        if isinstance(other, Ldict):
            self.evaluate()
            other.evaluate()
            return self.frozen.data == other.frozen.data
        if isinstance(other, Dict):
            self.evaluate()
            return self.frozen.data == other
        raise TypeError(f"Cannot compare {type(self)} and {type(other)}")
