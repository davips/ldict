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
from copy import deepcopy
from functools import reduce
from random import Random
from typing import Dict, TypeVar, Union, Callable

from orjson import dumps, OPT_SORT_KEYS

from garoupa import ø40
from ldict.appearance import ldict2txt, decolorize, ldict2dic
from ldict.apply import delete, application
from ldict.customjson import CustomJSONEncoder
from ldict.data import key2id
from ldict.exception import ReadOnlyLdict, WrongKeyType, WrongValueType, OverwriteException
from ldict.functionspace import FunctionSpace
from ldict.history import extend_history, rewrite_history
from ldict.lazy import islazy
from ldict.persistence import GLOBAL
from ldict.persistence.cached import cached

VT = TypeVar("VT")


class Ldict(UserDict, Dict[str, VT]):
    """Uniquely identified lazy dict for serializable pairs str->value

    (serializable in the 'orjson' sense)

    Usage:

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
        "id": "c._c0be2238b22114262680df425b85cac028be6",
        "ids": {
            "x": "Tz_d158c49297834fad67e6de7cdba3ea368aae4",
            "y": "lr_a377cc952bed4a78be99b0c57fd1ef9a9d002"
        },
        "x": 5,
        "y": 3
    }
    >>> d["y"]
    3
    >>> decolorize(str(d.history)) == '{c._c0be2238b22114262680df425b85cac028be6: {Tz_d158c49297834fad67e6de7cdba3ea368aae4, lr_a377cc952bed4a78be99b0c57fd1ef9a9d002}}'
    True
    >>> del d["x"]
    >>> d.show(colored=False)
    {
        "id": "lr_a377cc952bed4a78be99b0c57fd1ef9a9d002",
        "ids": {
            "y": "lr_a377cc952bed4a78be99b0c57fd1ef9a9d002"
        },
        "y": 3
    }
    >>> decolorize(str(d.history)) == '{lr_a377cc952bed4a78be99b0c57fd1ef9a9d002: None}'
    True
    >>> from ldict import ldict
    >>> ldict(x=123123, y=88).show(colored=False)
    {
        "id": "pp_009c55d4892401fa84d49936456d31c4e48fe",
        "ids": {
            "x": "a6_b90a521176a857d695e8404b5b7634d494da2",
            "y": "fj_7f5403c313a0a914feeb59fae9e60def40b4c"
        },
        "x": 123123,
        "y": 88
    }
    >>> ldict(y=88, x=123123).show(colored=False)  # Original values are order-insensitive.
    {
        "id": "pp_009c55d4892401fa84d49936456d31c4e48fe",
        "ids": {
            "y": "fj_7f5403c313a0a914feeb59fae9e60def40b4c",
            "x": "a6_b90a521176a857d695e8404b5b7634d494da2"
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
        "id": "hE756VJEI2rO7fD3c-hEX4hMB7TZsuLzkF84sOwe",
        "ids": {
            "w": "uKTTrcegTC-FUyhEj56XURPzkH.fTbFo4RK7M5M5",
            "z": "bLDj2EvLAT341.EPtWKlI-MnFxUJBi6bgQpYHIM8",
            "x": "a6_b90a521176a857d695e8404b5b7634d494da2",
            "y": "fj_7f5403c313a0a914feeb59fae9e60def40b4c"
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
    >>> from ldict import ø
    >>> d = ø >> {"x": value}
    >>> d.ids["x"]  # id (hosh) of the pair x→blob
    'UM_b2511f438c2c34d658372d3666b6c4411cc2d'
    >>> print(d.hoshes["x"] // "x-_0000000000000000000000000000000000000")  # id (hosh) of the value
    nO_6d3d2d399495b6545837334176b6c49bfbc2d
    """

    def __init__(self, /, _dictionary=None, identity=ø40, readonly=False, **kwargs):
        self.identity, self.readonly, self.digits, self.version = identity, readonly, identity.digits, identity.version
        self.blobs = {}
        self.hashes = {}
        self.hoshes = {}
        self.hosh = identity
        self.rho = identity.rho
        self.delete = identity.delete
        self.history = {}
        self.last = None
        self.rnd = Random()
        super().__init__()
        self.data.update(id=identity.id, ids={})
        self.update(**(_dictionary or {}), **kwargs)
        self.__name__ = self.id[:10]

    def __setitem__(self, key: str, value):
        if self.readonly:
            raise ReadOnlyLdict(f"Cannot change a readonly ldict ({self.id}).", key)
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        if callable(value):
            raise WrongValueType(f"A value for the field [{key}] cannot have type {type(value)}. "
                                 f"For (pseudo)inplace function application, use operator >>= instead")
        if isinstance(value, Ldict):
            value = value.clone(readonly=True)

        if key in self.data:
            del self[key]

        if hasattr(value, "hosh"):
            if isinstance(value, Ldict):
                self.hashes[key] = value.hosh
                self.hoshes[key] = self.hashes[key] ** key2id(key, self.digits)
            else:
                self.hoshes[key] = value.hosh
        else:
            self.blobs[key] = dumps(value, option=OPT_SORT_KEYS)
            self.hashes[key] = self.identity.h * self.blobs[key]
            self.hoshes[key] = self.hashes[key] ** key2id(key, self.digits)

        self.hosh *= self.hoshes[key]
        self.data[key] = value
        self.data["id"] = self.hosh.id
        self.data["ids"][key] = self.hoshes[key].id
        extend_history(self, self.hoshes[key])

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
        if self.readonly:
            raise ReadOnlyLdict(f"Cannot change a readonly ldict ({self.id}).", key)
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
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
        rewrite_history(self, deleted)

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
        """
        >>> from ldict import ldict
        >>> ldict(x=134124, y= 56).show(colored=False)
        {
            "id": "qa_4be7715daafe4d3ea3492c7570286388be26a",
            "ids": {
                "x": "PW_da3502210fa15a89fa109f3232ade04627449",
                "y": "Df_2ea4756cabb67532b829a24e4e7a729c77e11"
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
        """
        Usage:

        >>> from ldict import ldict
        >>> from ldict import decolorize
        >>> out = ldict(x=134124, y= 56).all
        >>> decolorize(out)
        '{\\n    "id": "qa_4be7715daafe4d3ea3492c7570286388be26a",\\n    "ids": {\\n        "x": "PW_da3502210fa15a89fa109f3232ade04627449",\\n        "y": "Df_2ea4756cabb67532b829a24e4e7a729c77e11"\\n    },\\n    "x": 134124,\\n    "y": 56\\n}'
        """
        return self.__repr__(all=True)

    def __rrshift__(self, other: Union[Dict, Callable, FunctionSpace]):
        if isinstance(other, Dict) and not isinstance(other, Ldict):
            return Ldict(other) >> self
        if callable(other):
            return FunctionSpace(other, self)
        return NotImplemented

    def __rshift__(self, other: Union[Dict, Callable, FunctionSpace], config={}):
        from ldict.cfg import cfg
        if isinstance(other, Dict):
            # Insertion of dict-like.
            clone = self.clone()
            for k, v in other.items():
                if v is None:
                    delete(self, clone, k)
                elif callable(v):
                    raise WrongValueType(f"Value (for field {k}) cannot have type {type(v)}")
                elif k not in ["id", "ids"]:
                    if k in self.data:
                        raise OverwriteException(f"Cannot overwrite field ({k}) via value insertion through >>")
                    clone[k] = v
            return clone
        if isinstance(other, FunctionSpace):
            return reduce(operator.rshift, (self,) + other.functions)
        if isinstance(other, cfg):
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

    def clone(self, readonly=False):
        """
        >>> d1 = Ldict(x=5, y=7)
        >>> d2 = Ldict(x=5, y=7)
        >>> e = d1.clone()
        >>> del e["y"]
        >>> d1 == d2 and d1 != e
        True

        Parameters
        ----------
        readonly

        Returns
        -------

        """
        obj = ldict(identity=self.identity, readonly=readonly)
        obj.blobs = self.blobs.copy()
        obj.hashes = self.hashes.copy()
        obj.hoshes = self.hoshes.copy()
        obj.hosh = self.hosh
        obj.data = self.data.copy()
        obj.data["ids"] = self.data["ids"].copy()
        obj.history = deepcopy(self.history)
        obj.last = self.last
        obj.rnd = self.rnd  # Do not clone rnd generator. Ldict will be cloned
        return obj

    def evaluate(self):
        """
        Usage:

        >>> from ldict import ldict
        >>> f = lambda x: {"y": x+2}
        >>> d = ldict(x=3)
        >>> a = d >> f
        >>> a.show(colored=False)
        {
            "id": "LKJz3bzFi4xSmTxP8Xa-1ax7ku.xW4AU0sYuSnwe",
            "ids": {
                "y": "dUeu3VqRSv4UEz0sh3F-pzj7iFUxW4AU0sYuSnwe",
                "x": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002"
            },
            "y": "→(x)",
            "x": 3
        }
        >>> a.evaluate()
        >>> a.show(colored=False)
        {
            "id": "LKJz3bzFi4xSmTxP8Xa-1ax7ku.xW4AU0sYuSnwe",
            "ids": {
                "y": "dUeu3VqRSv4UEz0sh3F-pzj7iFUxW4AU0sYuSnwe",
                "x": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002"
            },
            "y": 5,
            "x": 3
        }

        Returns
        -------

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
        c = cached(self, GLOBAL["CACHE"])
        c = cached(self, GLOBAL["CACHE"]) >> other
        return cached(self, GLOBAL["CACHE"]) >> other

    @property
    def idc(self):
        """Colored id"""
        return self.hosh.idc

    @property
    def ids(self):
        return self.data["ids"]

    def __str__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if islazy(v):
                dic[k] = str(v)
        if not all:
            if len(self.ids) < 3:
                dic["ids"] = " ".join(self.ids.values())
            else:
                ids = list(self.ids.values())
                dic["ids"] = f"{ids[0]}... +{len(self) - 4} ...{ids[-1]}"
        return json.dumps(dic, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)

    @property
    def asdict(self):
        return ldict2dic(self, all=True)

    def __mul__(self, other):
        return FunctionSpace(other)


ldict = Ldict
