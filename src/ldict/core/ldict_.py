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
from copy import deepcopy
from functools import reduce
from random import Random
from typing import Dict, TypeVar, Union, Callable

from garoupa import ø40

from ldict.appearance import ldict2txt, decolorize, ldict2dict
from ldict.compression import pack
from ldict.config import GLOBAL
from ldict.core.history import extend_history, rewrite_history
from ldict.core.init import initialize, build_from_dict
from ldict.core.inspection import input_fields, extract_dicts, output_fields, implicit_input
from ldict.core.rshift import update_identity, create_lazies, handle_dict
from ldict.customjson import CustomJSONEncoder
from ldict.data import key2id
from ldict.exception import WrongKeyType, check_access
from ldict.lazy import islazy
from ldict.parameter.functionspace import FunctionSpace
from ldict.parameter.let import Let
from ldict.persistence.cached import cached

VT = TypeVar("VT")


class Ldict(UserDict, Dict[str, VT]):
    r"""Uniquely identified lazy dict for serializable (pickable) pairs str->value

    Usage:

    >>> from ldict import setup, ldict
    >>> setup(history=True)  # Keep history of ids of all applied functions.
    >>> ldict(y=88, x=123123) != ldict(x=88, y=123123)  # Ids of original values embbed the keys.
    True
    >>> ldict().show(colored=False)
    {
        "id": "0000000000000000000000000000000000000000",
        "ids": {}
    }
    >>> d = ldict(x=5, y=3)
    >>> d.show(colored=False)
    {
        "id": "Xt_6cc13095bc5b4c671270fbe8ec313568a8b35",
        "ids": {
            "x": ".T_f0bb8da3062cc75365ae0446044f7b3270977",
            "y": "XB_1cba4912b6826191bcc15ebde8f1b960282cd"
        },
        "x": 5,
        "y": 3
    }
    >>> d["y"]
    3
    >>> from garoupa import H
    >>> d.history == {H.fromid("Xt_6cc13095bc5b4c671270fbe8ec313568a8b35"): {H.fromid("XB_1cba4912b6826191bcc15ebde8f1b960282cd"), H.fromid(".T_f0bb8da3062cc75365ae0446044f7b3270977")}}
    True
    >>> del d["x"]
    >>> d.show(colored=False)
    {
        "id": "XB_1cba4912b6826191bcc15ebde8f1b960282cd",
        "ids": {
            "y": "XB_1cba4912b6826191bcc15ebde8f1b960282cd"
        },
        "y": 3
    }
    >>> d.history == {H.fromid("XB_1cba4912b6826191bcc15ebde8f1b960282cd"): None}
    True
    >>> from ldict import ldict
    >>> ldict(x=123123, y=88).show(colored=False)
    {
        "id": "dR_5b58200b12d6f162541e09c570838ef5a429e",
        "ids": {
            "x": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e",
            "y": "9X_c8cb257a04eba75c381df365a1e7f7e2dc660"
        },
        "x": 123123,
        "y": 88
    }
    >>> ldict(y=88, x=123123).show(colored=False)  # Original values are order-insensitive.
    {
        "id": "dR_5b58200b12d6f162541e09c570838ef5a429e",
        "ids": {
            "y": "9X_c8cb257a04eba75c381df365a1e7f7e2dc660",
            "x": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e"
        },
        "y": 88,
        "x": 123123
    }
    >>> ldict(y=88, x=123123) != ldict(x=88, y=123123)  # Ids of original values embbed the keys.
    True
    >>> d = ldict(x=123123, y=88)
    >>> e = d >> (lambda x: {"z": x**2}) >> (lambda x,y: {"w": x/y})
    >>> e.show(colored=False)
    {
        "id": "96PdbhpKgueRWa.LSQWcSSbr.ZMZsuLzkF84sOwe",
        "ids": {
            "w": "1--sDMlN-GuH4FUXhvPWNkyHmTOfTbFo4RK7M5M5",
            "z": ".JXmafqx65TZ-laengA5qxtk1fUJBi6bgQpYHIM8",
            "x": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e",
            "y": "9X_c8cb257a04eba75c381df365a1e7f7e2dc660"
        },
        "w": "→(x y)",
        "z": "→(x)",
        "x": 123123,
        "y": 88
    }
    >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x, y: {"w": x/y})
    >>> b = d >> (lambda x, y: {"w": x/y}) >> (lambda x: {"z": x**2})
    >>> a != b  # Calculated values are order-sensitive.
    True
    >>> value = "some content"
    >>> from ldict import Ø
    >>> dic = d.asdict  # Converting to dict
    >>> dic
    {'id': 'dR_5b58200b12d6f162541e09c570838ef5a429e', 'ids': {'x': '4W_3331a1c01e3e27831cf08b7bde9b865db7b2e', 'y': '9X_c8cb257a04eba75c381df365a1e7f7e2dc660'}, 'x': 123123, 'y': 88}
    >>> d2 = ldict(dic)  # Reconstructing from a dict
    >>> print(d2)
    {
        "id": "dR_5b58200b12d6f162541e09c570838ef5a429e",
        "x": 123123,
        "y": 88,
        "ids": "4W_3331a1c01e3e27831cf08b7bde9b865db7b2e 9X_c8cb257a04eba75c381df365a1e7f7e2dc660"
    }
    >>> decolorize(str(d.history))
    '{dR_5b58200b12d6f162541e09c570838ef5a429e: {9X_c8cb257a04eba75c381df365a1e7f7e2dc660, 4W_3331a1c01e3e27831cf08b7bde9b865db7b2e}}'
    >>> d2.history
    {}
    >>> d = Ø >> {"x": value}
    >>> d.ids["x"]  # id (hosh) of the pair x→blob
    'E1_f5604bf7c358c3ee985ced6d11d353606e862'
    >>> print(d.hoshes["x"] // "x-_0000000000000000000000000000000000000")  # id (hosh) of the value
    73_5f90a94416d6366c985c047821d353ba4e862
    >>> from ldict import ldict
    >>> from random import Random
    >>> d = ldict(x=3,y=4,z=5)
    >>> f = lambda x, y: {"w": x*y, "u": x/y, "y": x+y}
    >>> print(d >> f)
    {
        "id": "lrmvztCQumKtsNzdQawt-4Fiu7J1HYiMhE166Amm",
        "ids": "319KfPVu.Yv2BEg4vCfEwwHa1JCKIYiMhA166Amn... +3 ...1U_fdd682399a475d5365aeb336044f7b4270977",
        "w": "→(x y)",
        "u": "→(x y)",
        "y": "→(x y)",
        "x": 3,
        "z": 5
    }
    >>> f = lambda x, y, a=5, b=[1,2,3,...,10]: {"w": x*y, "u": x/y, "y": x+y}
    >>> print(d >> Random(0) >> f)
    {
        "id": "HnV-kW-I7J25bUX8j6qY.B.Nh4F4yEvHV-m-kBB4",
        "ids": "FecPy5VZTQicxlSxmzBRTNCKZdwNzEvHVWm-kBB5... +3 ...1U_fdd682399a475d5365aeb336044f7b4270977",
        "w": "→(b x y)",
        "u": "→(b x y)",
        "y": "→(b x y)",
        "x": 3,
        "z": 5
    }
    >>> from garoupa import ø
    >>> f = lambda x, y: {"w": x*y, "u": x/y, "y": x+y}
    >>> f.hosh = ø * "1234567890123456789012345678901234567890"
    >>> f.input_fields = ["x"]
    >>> (d >> f).id == (d.hosh * "1234567890123456789012345678901234567890").id
    True

    Parameters
    ----------
    _dictionary
    identity
        Identity element indicating the adopted group/digest size etc.
    readonly
    kwargs
    """

    def __init__(self, /, _dictionary=None, identity=ø40, readonly=False, let=None, **kwargs):
        if isinstance(_dictionary, Ldict):
            raise Exception("Cannot instantiate Ldict from another Ldict, please use ldict.clone().")
        dic = _dictionary or {}
        dic.update(kwargs)
        initialize(self, identity, readonly, let)
        super().__init__()
        if "id" in dic:
            build_from_dict(dic, self)
        else:
            self.data.update(id=identity.id, ids={})
            self.update(dic)

    def __setitem__(self, key: str, value):
        r"""
        >>> from pandas import DataFrame
        >>> from ldict import ldict
        >>> d = ldict(x= DataFrame([[1,2]]))
        >>> print(d)
        {
            "id": "5p_7db781815b66f412d0fca6ca5ca1642b31c12",
            "ids": "5p_7db781815b66f412d0fca6ca5ca1642b31c12",
            "x": "[[1 2]]"
        }
        >>> d["z"] = lambda x: x**2
        >>> d.z.to_numpy()
        array([[1, 4]])
        >>> d["x"] = lambda x,z: x+z
        >>> d.x.to_numpy()
        array([[2, 6]])
        """
        check_access(self.id, self.readonly, key)

        if callable(value):
            input, parameters, fhosh = input_fields(value, self.data, self.identity)
            create_lazies(value, input, [], [key], self.data, self.let, parameters, self.rnd, multi_output=False)
            self.hosh = update_identity([key], self.data, fhosh, self.hosh, self.hoshes, self.let)
            return

        if hasattr(value, "hosh"):
            if isinstance(value, Ldict):
                value = value.clone(readonly=True)
                self.hashes[key] = value.hosh
                self.hoshes[key] = self.hashes[key] ** key2id(key, self.digits)
            else:
                self.hoshes[key] = value.hosh
        else:
            self.blobs[key] = pack(value)
            self.hashes[key] = self.identity.h * self.blobs[key]
            self.hoshes[key] = self.hashes[key] ** key2id(key, self.digits)

        self.hosh = reduce(operator.mul, self.hoshes.values())
        self.data[key] = value
        self.data["id"] = self.hosh.id
        self.data["ids"][key] = self.hoshes[key].id
        self.last = extend_history(self.history, self.last, self.hoshes[key])

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise WrongKeyType(f"Key must be string, not {type(item)}.", item)
        if item not in self.data:
            raise KeyError(item)
        content = self.data[item]
        if islazy(content):
            self.data[item] = content()
        return self.data[item]

    def __delitem__(self, key):
        check_access(self.id, self.readonly, key)
        if key in self.blobs:
            del self.blobs[key]
            del self.hashes[key]
        deleted = self.hoshes.pop(key)
        self.hosh = self.identity
        for hosh in self.hoshes.values():
            self.hosh *= hosh
        del self.data[key]
        self.data["id"] = self.hosh.id
        del self.data["ids"][key]
        self.last = rewrite_history(self.history, self.last, deleted, self.hoshes)

    def __repr__(self, all=False):
        return ldict2txt(self, all)

    def __eq__(self, other):
        if isinstance(other, Ldict):
            return self.n == other.n
        return NotImplemented

    def __hash__(self):
        return hash(self.hosh)

    def __ne__(self, other):
        if isinstance(other, Ldict):
            return self.hosh != other.hosh
        return NotImplemented

    def __getattr__(self, item):
        if item in self:
            return self[item]
        return self.__getattribute__(item)

    def show(self, colored=True):
        r"""
        >>> from ldict import ldict
        >>> ldict(x=134124, y= 56).show(colored=False)
        {
            "id": "dq_d85091ef315b9ce0d5eb1a5aabb6e6434a97f",
            "ids": {
                "x": "gZ_37ee5e71c9cd4c9bde421cdb917e5c56f7ebe",
                "y": "Zs_c473399e77e6c2d2f69914891a488a3732bb0"
            },
            "x": 134124,
            "y": 56
        }
        """
        return print(self.all if colored else decolorize(self.all))

    @property
    def id(self):
        return self.hosh.id

    @property
    def n(self):
        return self.hosh.n

    @property
    def all(self):
        r"""
        Usage:

        >>> from ldict import ldict
        >>> from ldict import decolorize
        >>> out = ldict(x=134124, y= 56).all
        >>> decolorize(out)
        '{\n    "id": "dq_d85091ef315b9ce0d5eb1a5aabb6e6434a97f",\n    "ids": {\n        "x": "gZ_37ee5e71c9cd4c9bde421cdb917e5c56f7ebe",\n        "y": "Zs_c473399e77e6c2d2f69914891a488a3732bb0"\n    },\n    "x": 134124,\n    "y": 56\n}'
        """
        return self.__repr__(all=True)

    def __rrshift__(self, other: Union[Dict, Callable, FunctionSpace]):
        r"""
        >>> from ldict import ldict, Ø
        >>> print({"x":5} >> ldict())
        {
            "id": ".T_f0bb8da3062cc75365ae0446044f7b3270977",
            "ids": ".T_f0bb8da3062cc75365ae0446044f7b3270977",
            "x": 5
        }
        >>> print({"x":5} >> Ø >> (lambda x: {"y": x**2}))
        {
            "id": "6CrMO8u.l0Bf.Mw-a4-5OncDYWeLRgUAfdP7HEp4",
            "ids": "RsjNt2f4bnIPB7PhbP-nORX85XgLRgUAfdP7HEp4 .T_f0bb8da3062cc75365ae0446044f7b3270977",
            "y": "→(x)",
            "x": 5
        }
        """
        if isinstance(other, Dict):
            return Ldict(other) >> self
        if callable(other):
            return FunctionSpace(other, self)
        return NotImplemented

    def __rshift__(self, other: Union[Dict, Callable, Let, FunctionSpace, Random]):
        if isinstance(other, Dict):
            return handle_dict(clone := self.clone(), other) or clone
        if isinstance(other, FunctionSpace):
            return reduce(operator.rshift, (self,) + other.functions)
        if isinstance(other, Let):
            config = self.let.copy()
            config.update(other.config)
            return self.clone(let=config)
        if isinstance(other, Random):
            return self.clone(rnd=other)
        if isinstance(other, list):
            d = self
            for cache in other:
                d = cached(d, cache)
            return d
        if not callable(other):
            raise NotImplemented

        clone = self.clone()
        input, parameters, fhosh = input_fields(other, clone.data, clone.identity)
        dicts = extract_dicts(other)
        output = output_fields(other, dicts, parameters)
        implicit = implicit_input(other, dicts, parameters)
        create_lazies(other, input, implicit, output, clone.data, clone.let, parameters, clone.rnd, multi_output=True)
        clone.hosh = update_identity(output, clone.data, fhosh, clone.hosh, clone.hoshes, clone.let)
        clone.last = extend_history(clone.history, clone.last, clone.hosh)
        return clone

    def clone(self, readonly=None, let=None, rnd=None):
        r"""
        >>> d1 = Ldict(x=5, y=7)
        >>> d2 = Ldict(x=5, y=7)
        >>> e = d1.clone()
        >>> del e["y"]
        >>> d1 == d2 and d1 != e
        True
        """
        if readonly is None:
            readonly = self.readonly
        if let is None:
            let = self.let
        if rnd is None:
            # Do not clone rnd generator. Ldict will be cloned.
            rnd = self.rnd
        obj = Ldict(identity=self.identity, readonly=readonly, let=let)
        obj.blobs = self.blobs.copy()
        obj.hashes = self.hashes.copy()
        obj.hoshes = self.hoshes.copy()
        obj.hosh = self.hosh
        obj.data = self.data.copy()
        obj.data["ids"] = self.data["ids"].copy()
        obj.history = deepcopy(self.history)
        obj.last = self.last
        obj.rnd = rnd
        return obj

    def evaluate(self):
        r"""
        Usage:

        >>> from ldict import ldict
        >>> f = lambda x: {"y": x+2}
        >>> d = ldict(x=3)
        >>> a = d >> f
        >>> a.show(colored=False)
        {
            "id": "tFkvrmyHlXSnstVFIFktJjD7K91yW4AU0sYuSnwe",
            "ids": {
                "y": "BZz1P5xA5r0gfAqOtHySEb.m0HTxW4AU0sYuSnwe",
                "x": "WB_e55a47230d67db81bcc1aecde8f1b950282cd"
            },
            "y": "→(x)",
            "x": 3
        }
        >>> a.evaluate()
        >>> a.show(colored=False)
        {
            "id": "tFkvrmyHlXSnstVFIFktJjD7K91yW4AU0sYuSnwe",
            "ids": {
                "y": "BZz1P5xA5r0gfAqOtHySEb.m0HTxW4AU0sYuSnwe",
                "x": "WB_e55a47230d67db81bcc1aecde8f1b950282cd"
            },
            "y": 5,
            "x": 3
        }
        """
        for field in self:
            _ = self[field]

    def __rxor__(self, other: Union[Dict, Callable]):
        if isinstance(other, Dict) and not isinstance(other, Ldict):
            return Ldict(other) >= self
        return NotImplemented

    def __xor__(self, other: Union[Dict, Callable]):
        # from ldict import Empty
        # if isinstance(other, FunctionSpace) and isinstance(other[0], Empty):
        #     raise EmptyNextToGlobalCache("Cannot use ø after ^ due to Python precedence rules.")
        return cached(self, GLOBAL["cache"]) >> other

    @property
    def idc(self):
        """Colored id"""
        return self.hosh.idc

    @property
    def ids(self):
        return self.data["ids"]

    def __str__(self, all=False):
        return json.dumps(ldict2dict(self, all), indent=4, ensure_ascii=False, cls=CustomJSONEncoder)

    @property
    def asdict(self):
        r"""
        >>> from ldict import ldict
        >>> ldict(x=3, y=5).asdict
        {'id': 'Xt_a63010fa2b5b4c671270fbe8ec313568a8b35', 'ids': {'x': 'WB_e55a47230d67db81bcc1aecde8f1b950282cd', 'y': '0U_e2a86ff72e226d5365aea336044f7b4270977'}, 'x': 3, 'y': 5}
        """
        return ldict2dict(self, all=True)

    def __mul__(self, other):
        return FunctionSpace(other)
