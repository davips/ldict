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

from garoupa import ø40

from idict.frozenidentifieddict import FrozenIdentifiedDict
from ldict.core.base import AbstractMutableLazyDict
from ldict.core.rshift import handle_dict, lazify
from ldict.exception import WrongKeyType
from ldict.frozenlazydict import FrozenLazyDict
from ldict.parameter.functionspace import FunctionSpace
from ldict.parameter.let import Let

VT = TypeVar("VT")


class Idict(AbstractMutableLazyDict):
    """Mutable lazy identified dict for serializable (picklable) pairs str->value

    Usage:

    >>> from idict import idict
    >>> print(idict())
    {
        "id": "0000000000000000000000000000000000000000",
        "ids": {}
    }
    >>> d = idict(x=5, y=3)
    >>> print(d)
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
    >>> print(idict(x=123123, y=88))
    {
        "x": 123123,
        "y": 88,
        "id": "dR_5b58200b12d6f162541e09c570838ef5a429e",
        "ids": {
            "x": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e",
            "y": "9X_c8cb257a04eba75c381df365a1e7f7e2dc660"
        }
    }
    >>> print(idict(y=88, x=123123))
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
    >>> print(e)
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
    >>> print(d)
    {
        "id": "0000000000000000000000000000000000000000",
        "ids": {
            "x": "lU_2bc203cfa982e84748e044ad5f3a86dcf97ff"
        },
        "x": "more content"
    }
    >>> del e["z"]
    >>> e
    >>> e["x"] = 77
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, id=None, ids=None, rnd=None, identity=ø40, _cloned=None, **kwargs):
        self.identity = identity
        self.frozen: FrozenIdentifiedDict = FrozenIdentifiedDict(_dictionary, id, ids, rnd, identity, _cloned, **kwargs)

    @property
    def id(self):
        return self.frozen.id

    @property
    def hosh(self):
        return self.frozen.hosh

    @property
    def blobs(self):
        return self.frozen.blobs

    @property
    def hashes(self):
        return self.frozen.hashes

    @property
    def hoshes(self):
        return self.frozen.hoshes

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        data, blobs, hashes, hoshes = self.data.copy(), self.blobs.copy(), self.blobs.copy(), self.blobs.copy()
        for coll in [data, blobs, hashes, hoshes]:
            del coll[key]
        hosh = reduce(operator.mul, [self.identity] + list(self.hoshes.values()))
        self.frozen = self.frozen.clone(data, _cloned=dict(blobs=blobs, hashes=hashes, hoshes=hoshes, hosh=hosh))

    def __getattr__(self, item):
        return self.frozen[item]

    def __repr__(self):
        return repr(self.frozen)

    def __str__(self):
        return str(self.frozen)

    def evaluate(self):
        """
        >>> from idict import idict
        >>> f = lambda x: {"y": x+2}
        >>> d = idict(x=3)
        >>> a = d >> f
        >>> print(a)
        {
            "x": 3,
            "y": "→(x)"
        }
        >>> a.evaluate()
        >>> print(a)
        {
            "x": 3,
            "y": 5
        }
        """
        self.frozen.evaluate()

    @property
    def asdict(self):
        """
        >>> from idict import idict
        >>> d = idict(x=3, y=5)
        >>> idict(x=7, y=8, d=d).asdict
        {'x': 7, 'y': 8, 'd': {'x': 3, 'y': 5}}
        """
        return self.frozen.asdict

    def clone(self, data=None, rnd=None, _cloned=None):
        cloned_internals = _cloned or dict(blobs=self.blobs, hashes=self.hashes, hoshes=self.hoshes, hosh=self.hosh)
        return Idict(data or self.data, rnd=rnd or self.rnd, identity=self.identity, _cloned=cloned_internals)

    def __rrshift__(self, other: Union[Dict, Callable, FunctionSpace]):
        if isinstance(other, Dict):
            return Idict(other) >> self
        if callable(other):
            return FunctionSpace(other, self)
        return NotImplemented

    def __rshift__(self, other: Union[Dict, 'Idict', Callable, Let, FunctionSpace, Random]):
        from idict import Empty
        if isinstance(other, Random):
            return self.clone(rnd=other)
        if isinstance(other, Empty):
            return self
        if isinstance(other, Idict):
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
        return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        # REMINDER: idict and cdict should compared ids
        self.evaluate()
        if isinstance(other, (FrozenLazyDict, Ldict)):
            other.evaluate()
            return self.data == other.data
        if isinstance(other, Dict):
            return self.frozen.data == other
        raise TypeError(f"Cannot compare {type(self)} and {type(other)}")
