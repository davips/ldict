#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the dictid project.
#  Please respect the license - more about this in the section (*) below.
#
#  dictid is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  dictid is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with dictid.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.

# Initially based on https://stackoverflow.com/a/64323140/9681577
import hashlib
import re
from collections import abc
from functools import cached_property
from inspect import signature, getsourcelines
from itertools import chain
from typing import Dict as Dict_, Iterator, MutableMapping, TypeVar, Iterable

from dictid.base62 import b62enc
from orjson import dumps, OPT_SORT_KEYS

KT = TypeVar('KT')
VT = TypeVar('VT')


class Dict(MutableMapping[KT, VT]):

    def __init__(self, _dictionary=None, /, **kwargs) -> None:
        """Uniquely Identified dict of hashable items."""
        self.data: Dict_[str, VT] = {}
        if _dictionary is not None:
            self.update(_dictionary)
        self.bytes = dumps(self.data, option=OPT_SORT_KEYS)
        self.md5 = hashlib.md5(self.bytes)
        self.bid = self.md5.digest()
        self.n = int.from_bytes(self.bid, 'big')  # Spent 912ns up to this point.
        kwargs["n"] = self.n
        if kwargs:
            self.update(kwargs)

    @cached_property
    def hid(self):
        return self.md5.hexdigest()  # Extra 290ns.

    @cached_property
    def id(self):
        return b62enc(self.n)  # Spent 5.72µs up to this point.

    def __getitem__(self, field: KT) -> VT:
        if field in self.data:
            content = self.data[field]
            if callable(content):
                return self.data[field](**self.getargs(content))
            else:
                return self.data[field]
        raise KeyError(field)

    def __rshift__(self, f):
        """Used for multiple return values, or to avoid inplace update."""
        returns = [line for line in getsourcelines(f)[0] if "return" in line]
        if len(returns) != 1:
            raise Exception("A single 'return <dict>' statement is expected. Not", len(returns))

        rx = r"(?:[\"'])([a-zA-Z]+[a-zA-Z0-9_]*)(?:[\"'])"
        output_fields = re.findall(rx, returns[0])
        fargs = signature(f).parameters.keys()
        self.update({k: self.trigger(k, f, fargs) for k in output_fields})
        return self

    def getargs(self, f, fargs=None):
        fargs = fargs or signature(f).parameters.keys()
        dic = {}
        for k in fargs:
            if k not in self:
                print(self)
                raise Exception(f"Missing field {k} needed by {f} to calculate field {field}.")
            dic[k] = self[k]
        return dic

    def trigger(self, field, f, fargs):
        def closure():
            dic = self.getargs(f, fargs)
            self.update(**f(**dic))
            return self[field]

        return closure

    def __hash__(self):
        return self.n

    def __str__(self):
        return str(self.data)

    def __eq__(self, other):
        if isinstance(other, Dict):
            return self.n == other.n
        return NotImplemented

    def __contains__(self, field: KT) -> bool:
        return field in self.data

    def __delitem__(self, field: KT) -> None:
        del self.data[field]

    def __getattr__(self, item):
        return self[item]

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[KT]:
        return chain(iter(self.data), ["n"])

    def __setitem__(self, field: KT, value: VT) -> None:
        self.data[field] = value

    @classmethod
    def fromkeys(cls, iterable: Iterable[KT], value: VT) -> "Dict":
        """Create a new dictionary with keys from `iterable` and values set to `value`.

        Args:
            iterable: A collection of keys.
            value: The default value. It defaults to None.
            All of the values refer to just a single instance,
            so it generally doesn’t make sense for value to be a mutable object such as an empty list.
            To get distinct values, use a dict comprehension instead.

        Returns:
            A new instance of Dict.
        """
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def update(self, other=(), /, **kwds) -> None:
        """Update the dictionary with the key/value pairs from other, overwriting existing keys. Return None."""
        if isinstance(other, abc.Mapping):
            for key in other:
                self.data[key] = other[key]
        elif hasattr(other, "keys"):
            for key in other.keys():
                self.data[key] = other[key]
        else:
            for key, value in other:
                self.data[key] = value
        for key, value in kwds.items():
            self.data[key] = value
