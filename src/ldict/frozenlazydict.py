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
from collections import UserDict
from functools import reduce
from random import Random
from typing import Dict, TypeVar, Union, Callable

from ldict import FunctionSpace
from ldict.apply import application
from ldict.customjson import CustomJSONEncoder
from ldict.exception import WrongKeyType, WrongValueType, OverwriteException, ReadOnlyLdict
from ldict.lazyval import LazyVal
from ldict.persistence.cached import cached

VT = TypeVar("VT")


class FrozenLazyDict(UserDict, Dict[str, VT]):
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
    >>> e.show(colored=False)
    {
        "w": "→(x y)",
        "z": "→(x)",
        "x": 123123,
        "y": 88
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
    """

    def __init__(self, /, _dictionary=None, **kwargs):
        self.rnd = Random()
        super().__init__()
        self.data.update(_dictionary or kwargs)

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
        txt = json.dumps(self, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
        return txt.replace("\"«", "").replace("»\"", "")

    __str__ = __repr__

    def evaluate(self):
        """
        >>> from ldict import ldict
        >>> f = lambda x: {"y": x+2}
        >>> d = ldict(x=3)
        >>> a = d >> f
        >>> a
        {
            "y": "→(x)",
            "x": 3
        }
        >>> a.evaluate()
        >>> a
        {
            "y": 5,
            "x": 3
        }
        """
        for field in self:
            v = self[field]
            if isinstance(v, FrozenLazyDict):
                v.evaluate()

    @property
    def asdict(self):
        """
        >>> from ldict import ldict
        >>> ldict(x=3, y=5).asdict
        {'x': 3, 'y': 5}

        Returns
        -------

        """
        self.evaluate()
        return self.data.copy()

    def __rrshift__(self, other: Union[Dict, Callable, FunctionSpace]):
        """
        >>> from ldict import ldict, Ø
        >>> print({"x":5} >> ldict())
        {
            "id": "Tz_d158c49297834fad67e6de7cdba3ea368aae4",
            "ids": "Tz_d158c49297834fad67e6de7cdba3ea368aae4",
            "x": 5
        }
        >>> print({"x":5} >> Ø >> (lambda x: {"y": x**2}))
        {
            "id": "CY2WCsPnSAkwXoLXOFAY3Cl5oGiLRgUAfdP7HEp4",
            "ids": "KXZKAhHcSArn2fw9R-0hx4HazI9LRgUAfdP7HEp4 Tz_d158c49297834fad67e6de7cdba3ea368aae4",
            "y": "→(x)",
            "x": 5
        }

        Parameters
        ----------
        other

        Returns
        -------

        """
        if isinstance(other, Dict):
            return FrozenLazyDict(other) >> self
        if callable(other):
            return FunctionSpace(other, self)
        return NotImplemented

    def __rshift__(self, other: Union[Dict, Callable, FunctionSpace, Random], config={}):
        if isinstance(other, Dict):
            # Insertion of dict-like.
            clone = self.clone()
            for k, v in other.items():
                if v is None:
                    del clone.data[k]
                elif callable(v):
                    raise WrongValueType(f"Value (for field {k}) cannot have type {type(v)}")
                elif k not in ["id", "ids"]:
                    if k in self.data:
                        raise OverwriteException(f"Cannot overwrite field ({k}) via value insertion through >>")
                    clone[k] = v
            return clone
        if isinstance(other, FunctionSpace):
            return reduce(operator.rshift, (self,) + other.functions)
        if other.__class__.__name__ == "cfg":
            from ldict.cfg import Ldict_cfg
            d = Ldict_cfg(self, other.config)
            if other.f:
                d >>= other.f
            return d
        if isinstance(other, Random):
            (clone := self.clone()).rnd = other
            return clone
        if isinstance(other, list):
            d = self
            for cache in other:
                d = cached(d, cache)
            return d
        if not callable(other):
            raise WrongValueType(f"Value passed to >> should be callable or dict-like, not {type(other)}")
        clone = self.clone()
        return application(self, clone, other, config, clone.rnd)
