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
from json import dumps
from random import Random
from typing import Dict, TypeVar, Union, Callable

from garoupa import ø40
from orjson import OPT_SORT_KEYS

from idict.compression import pack
from idict.data import key2id
from idict.rshift import application
from ldict.core.base import AbstractLazyDict
from ldict.frozenlazydict import FrozenLazyDict
from ldict.parameter.functionspace import FunctionSpace
from ldict.parameter.let import Let

VT = TypeVar("VT")


class FrozenIdentifiedDict(AbstractLazyDict):
    """Immutable lazy universally identified dict for serializable (picklable) pairs str->value

    Usage:

    >>> from idict.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> idict()
    {
        "id": "0000000000000000000000000000000000000000",
        "ids": {}
    }
    >>> d = idict(x=5, y=3)
    >>> d
    {
        "x": 5,
        "y": 3,
        "id": "Xt_6cc13095bc5b4c671270fbe8ec313568a8b35",
        "ids": {
            "x": ".T_f0bb8da3062cc75365ae0446044f7b3270977",
            "y": "XB_1cba4912b6826191bcc15ebde8f1b960282cd"
        }
    }
    >>> d["y"]
    3
    >>> idict(x=123123, y=88)
    {
        "x": 123123,
        "y": 88,
        "id": "dR_5b58200b12d6f162541e09c570838ef5a429e",
        "ids": {
            "x": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e",
            "y": "9X_c8cb257a04eba75c381df365a1e7f7e2dc660"
        }
    }
    >>> idict(y=88, x=123123)
    {
        "y": 88,
        "x": 123123,
        "id": "dR_5b58200b12d6f162541e09c570838ef5a429e",
        "ids": {
            "y": "9X_c8cb257a04eba75c381df365a1e7f7e2dc660",
            "x": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e"
        }
    }
    >>> d = idict(x=123123, y=88)
    >>> d2 = d >> (lambda x: {"z": x**2})
    >>> d2.hosh == d2.identity * d2.ids["z"] * d2.ids["x"] * d2.ids["y"]
    True
    >>> e = d2 >> (lambda x,y: {"w": x/y})
    >>> e
    {
        "w": "→(x y)",
        "z": "→(x)",
        "x": 123123,
        "y": 88,
        "id": "96PdbhpKgueRWa.LSQWcSSbr.ZMZsuLzkF84sOwe",
        "ids": {
            "w": "1--sDMlN-GuH4FUXhvPWNkyHmTOfTbFo4RK7M5M5",
            "z": ".JXmafqx65TZ-laengA5qxtk1fUJBi6bgQpYHIM8",
            "x": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e",
            "y": "9X_c8cb257a04eba75c381df365a1e7f7e2dc660"
        }
    }
    >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x, y: {"w": x/y})
    >>> b = d >> (lambda x, y: {"w": x/y}) >> (lambda x: {"z": x**2})
    >>> dic = d.asdict  # Converting to dict
    >>> dic
    {'x': 123123, 'y': 88, 'id': 'dR_5b58200b12d6f162541e09c570838ef5a429e', 'ids': {'x': '4W_3331a1c01e3e27831cf08b7bde9b865db7b2e', 'y': '9X_c8cb257a04eba75c381df365a1e7f7e2dc660'}}
    >>> d2 = idict(dic)  # Reconstructing from a dict
    >>> print(d2)
    {
        "x": 123123,
        "y": 88,
        "id": "dR_5b58200b12d6f162541e09c570838ef5a429e",
        "ids": {
            "x": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e",
            "y": "9X_c8cb257a04eba75c381df365a1e7f7e2dc660"
        }
    }
    >>> d == d2
    True
    >>> from idict import Ø
    >>> d = idict() >> {"x": "more content"}
    >>> d
    {
    }
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, id=None, ids=None, rnd=None, identity=ø40, _cloned=None, **kwargs):
        self.rnd = rnd
        self.identity = identity
        data = _dictionary or {}
        data.update(kwargs)

        if _cloned:
            self.blobs = _cloned["blobs"]
            self.hashes = _cloned["hashes"]
            self.hoshes = _cloned["hoshes"]
            self.hosh = _cloned["hosh"]
        else:
            self.blobs = {}
            self.hashes = {}
            if "id" in data:
                if id:  # pragma: no cover
                    raise Exception(f"Conflicting 'id' values: {id} and {data['id']}")
                id = data.pop("id")
            if "ids" in data:
                if ids:  # pragma: no cover
                    raise Exception(f"Conflicting 'ids' values: {ids} and {data['ids']}")
                ids = data.pop("ids")

            if id:
                if ids is None:  # pragma: no cover
                    raise Exception(f"'id' {id} given, but 'ids' is missing.")
                self.hoshes = {k: identity * v for k, v in ids.items()}
            else:
                self.hoshes = {}
                for k, v in data.items():
                    if isinstance(v, FrozenIdentifiedDict):
                        self.hashes[k] = v.hosh
                        self.hoshes[k] = self.hashes[k] ** key2id(k, identity.digits)
                    else:
                        self.blobs[k] = pack(v)
                        self.hashes[k] = self.identity.h * self.blobs[k]
                        self.hoshes[k] = self.hashes[k] ** key2id(k, identity.digits)
            self.hosh = reduce(operator.mul, [identity] + list(self.hoshes.values()))

        if id is None:
            id = self.hosh.id
            ids = {k: v.id for k, v in self.hoshes.items()}

        # Store as immutable lazy dict.
        self.frozen = FrozenLazyDict(data, id=id, ids=ids, rnd=rnd)
        self.data = self.frozen.data
        self.id = self.hosh.id

    def __getitem__(self, item):
        return self.frozen[item]

    def __setitem__(self, key: str, value):
        self.frozen[key] = value

    def __delitem__(self, key):
        del self.frozen[key]

    def __getattr__(self, item):
        return getattr(self.frozen, item)

    def __repr__(self):
        return repr(self.frozen)

    __str__ = __repr__

    def evaluate(self):
        """
        >>> from idict.frozenidentifieddict import FrozenIdentifiedDict as idict
        >>> f = lambda x: {"y": x+2}
        >>> d = idict(x=3)
        >>> a = d >> f
        >>> a
        {
            "y": "→(x)",
            "x": 3,
            "id": "tFkvrmyHlXSnstVFIFktJjD7K91yW4AU0sYuSnwe",
            "ids": {
                "y": "BZz1P5xA5r0gfAqOtHySEb.m0HTxW4AU0sYuSnwe",
                "x": "WB_e55a47230d67db81bcc1aecde8f1b950282cd"
            }
        }
        >>> a.evaluate()
        >>> a
        {
            "y": 5,
            "x": 3,
            "id": "tFkvrmyHlXSnstVFIFktJjD7K91yW4AU0sYuSnwe",
            "ids": {
                "y": "BZz1P5xA5r0gfAqOtHySEb.m0HTxW4AU0sYuSnwe",
                "x": "WB_e55a47230d67db81bcc1aecde8f1b950282cd"
            }
        }
        """
        self.frozen.evaluate()

    @property
    def asdict(self):
        """
        >>> from idict.frozenidentifieddict import FrozenIdentifiedDict as idict
        >>> d = idict(x=3, y=5)
        >>> d.id
        'Xt_a63010fa2b5b4c671270fbe8ec313568a8b35'
        >>> e = idict(x=7, y=8, d=d)
        >>> e.asdict
        {'x': 7, 'y': 8, 'd': {'x': 3, 'y': 5, 'id': 'Xt_a63010fa2b5b4c671270fbe8ec313568a8b35', 'ids': {'x': 'WB_e55a47230d67db81bcc1aecde8f1b950282cd', 'y': '0U_e2a86ff72e226d5365aea336044f7b4270977'}}, 'id': 'AN_650bae25143e28c5489bfbc806f5fb55c6fdc', 'ids': {'x': 'lX_9e55978592eeb1caf8778e34d26f5fd4cc8c8', 'y': '6q_07bbf68ac6eb0f9e2da3bda1665567bc21bde', 'd': '8s_1ccd1655bae1d9e91270e5eddc31351eb8b35'}}
        >>> d.hosh ** key2id("d", d.identity.digits) == e.hoshes["d"]
        True
        """
        return self.frozen.asdic

    def __rrshift__(self, other: Union[Dict, Callable, FunctionSpace]):
        if isinstance(other, Dict):
            return FrozenIdentifiedDict(other) >> self
        if callable(other):
            return FunctionSpace(other, self)
        return NotImplemented

    def __rshift__(self, other: Union[Dict, AbstractLazyDict, Callable, Let, FunctionSpace, Random]):
        if isinstance(other, Random):
            return self.clone(rnd=other)
        if isinstance(other, FunctionSpace):
            return reduce(operator.rshift, (self,) + other.functions)
        if callable(other):
            return application(self, other, other, self.identity)
        if isinstance(other, Let):
            return application(self, other, other.f, dumps(other.config, option=OPT_SORT_KEYS))

        # if isinstance(other, FrozenIdentifiedDict):
        #     return self.clone(ihandle_dict(self.frozen, other, other.rnd), other.rnd)
        # if isinstance(other, AbstractLazyDict):
        #     return self.clone(ihandle_dict(self.frozen, other, other.rnd), other.rnd)
        # if isinstance(other, Dict):
        #     return self.clone(handle_dict(self.data, other, self.rnd))
        return NotImplemented

    def clone(self, data=None, rnd=None, _cloned=None):
        """Clone with a new rnd object."""
        cloned_internals = _cloned or dict(blobs=self.blobs, hashes=self.hashes, hoshes=self.hoshes, hosh=self.hosh)
        return FrozenIdentifiedDict(data or self.data, rnd=rnd or self.rnd, _cloned=cloned_internals)

    def __eq__(self, other):
        return self.hosh == other.hosh

    def __ne__(self, other):
        return self.hosh != other.hosh

    def __hash__(self):
        return hash(self.hosh)
