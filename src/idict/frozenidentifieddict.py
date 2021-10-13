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

from garoupa import ø40

from ldict.core.base import AbstractLazyDict
from ldict.core.rshift import handle_dict, lazify
from ldict.customjson import CustomJSONEncoder
from ldict.exception import WrongKeyType, ReadOnlyLdict
from ldict.lazyval import LazyVal
from ldict.parameter.functionspace import FunctionSpace
from ldict.parameter.let import Let

VT = TypeVar("VT")


class FrozenIdentifiedDict(AbstractLazyDict):
    """Immutable lazy universally identified dict for serializable (picklable) pairs str->value

    Usage:

    >>> from idict.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> idict()
    {}
    >>> d = idict(x=5, y=3)
    >>> d
    {
        "x": 5,
        "y": 3
    }
    >>> d["y"]
    3
    >>> idict(x=123123, y=88)
    {
        "x": 123123,
        "y": 88
    }
    >>> idict(y=88, x=123123)
    {
        "y": 88,
        "x": 123123
    }
    >>> d = idict(x=123123, y=88)
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
    >>> d2 = idict(dic)  # Reconstructing from a dict
    >>> print(d2)
    {
        "x": 123123,
        "y": 88
    }
    >>> from idict import Ø
    >>> d = idict() >> {"x": "more content"}
    >>> d
    {
        "x": "more content"
    }
    """

    def __init__(self, /, _dictionary=None, rnd=None, identity=ø40, _cloned=None, **kwargs):
        self.rnd = rnd
        super().__init__()
        self.data = _dictionary or kwargs  # TODO: handle incomming ids
        if _cloned:
            self.hashes = _cloned["hashes"]
            self.hoshes = _cloned["hoshes"]
            self.blobs = _cloned["blobs"]
        else:
            self.hashes = _cloned["hashes"]
            self.hoshes = _cloned["hoshes"]
            self.blobs = _cloned["blobs"]
        self.hosh = reduce(operator.mul, self.hoshes)

    # def __init__(self, /, _dictionary=None, identity=ø40, readonly=False, **kwargs):
    #     dic = _dictionary or {}
    #     self.readonly, self.digits, self.version = readonly, identity.digits, identity.version
    #     self.rho, self.delete = identity.rho, identity.delete
    #     self.hosh = self.identity = identity
    #     self.blobs, self.hashes, self.hoshes = {}, {}, {}
    #     self.history, self.last = {}, None
    #     self.rnd = Random()
    #     dic.update(kwargs)
    #     super().__init__()
    #     if id := self.data.get("id", False) or dic.get("id", False):
    #         if not (ids := self.data.pop("ids", False) or dic.pop("ids", False)):
    #             raise MissingIds(f"id {id} provided but ids missing while importing dict-like")
    #         if not isinstance(id, str):
    #             raise WrongId(f"id {id} provided should be str, not {type(id)}")
    #         self.hosh *= id
    #         self.hoshes.update(ids)
    #         self.data.update(dic)
    #         self.data["ids"] = ids.copy()
    #     else:
    #         self.data.update(id=identity.id, ids={})
    #         self.update(dic)
    #     self.__name__ = self.id[:10]  # TODO: useful?

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
            if isinstance(v, FrozenIdentifiedDict):
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

    def clone(self, data=None, rnd=None):
        """Same lazy content with (optional) new data or rnd object."""
        return FrozenIdentifiedDict(self.data if data is None else data, rnd=rnd or self.rnd)

    def __rrshift__(self, other: Union[Dict, Callable, FunctionSpace]):
        if isinstance(other, Dict):
            return FrozenIdentifiedDict(other) >> self
        if callable(other):
            return FunctionSpace(other, self)
        return NotImplemented

    def __rshift__(self, other: Union[Dict, 'Ldict', Callable, Let, FunctionSpace, Random]):
        if isinstance(other, Random):
            return self.clone(rnd=other)
        if isinstance(other, FrozenIdentifiedDict):
            return self.clone(handle_dict(self.data, other, other.rnd), other.rnd)
        if isinstance(other, Dict):
            return self.clone(handle_dict(self.data, other, self.rnd))
        if isinstance(other, FunctionSpace):
            return reduce(operator.rshift, (self,) + other.functions)
        if callable(other) or isinstance(other, Let):
            lazies = lazify(self.data, output_field="extract", f=other, rnd=self.rnd, multi_output=True)
            data = self.data.copy()
            data.update(lazies)
            return self.clone(data)
        raise NotImplemented
