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
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
from collections import UserDict
from copy import deepcopy
from typing import Dict, TypeVar, Union, Callable

from orjson import dumps, OPT_SORT_KEYS

from garoupa import ø40
from ldict_modules.appearance import ldict2txt, decolorize
from ldict_modules.apply import delete, output_fields, input_fields, substitute
from ldict_modules.data import fhosh
from ldict_modules.exception import FunctionTypeException
from ldict_modules.history import extend_history, rewrite_history
from ldict_modules.lazy import Lazy

VT = TypeVar("VT")


class Ldict(UserDict, Dict[str, VT]):
    """Uniquely identified lazy dict for serializable pairs str->value

    (serializable in the 'orjson' sense)

    Usage:

    >>> ø40*"BJ_b41cd0efbf48138cf72cc0cd5f888e779cd84" *"zG_fe3f7ea767dcf8dc65d39bfa9f2c07ef023d0"
    >>> ø40*"DT_192526ef97b9b51aced6f4ca2e9cdfeacd07a"*"ww_9a2639a78f6b564f9e1967fdc028b57cd00fa"
    >>> ldict(y=88, x=123123) != ldict(x=88, y=123123)  # Ids of original values embbed the keys.

    # >>> ldict().show(colored=False)
    # {
    #     "id": "0000000000000000000000000000000000000000",
    #     "ids": {}
    # }
    # >>> d = ldict(x=5, y=3)
    # >>> d.show(colored=False)
    # {
    #     "id": "WZ_0fa02ba42fc8ac070fab8cc9f4ec1f19f145d",
    #     "ids": {
    #         "x": "g8_70f95e0d9b4e6e2647d114311069bdf618013",
    #         "y": "GR_aff52c9783a5c3e0c7d92888e4836132e934a"
    #     },
    #     "x": 5,
    #     "y": 3
    # }
    # >>> d["y"]
    # 3
    # >>> d.history == {'WZ_0fa02ba42fc8ac070fab8cc9f4ec1f19f145d': {"g8_70f95e0d9b4e6e2647d114311069bdf618013", "GR_aff52c9783a5c3e0c7d92888e4836132e934a"}}
    # True
    # >>> del d["x"]
    # >>> d.show(colored=False)
    # {
    #     "id": "GR_aff52c9783a5c3e0c7d92888e4836132e934a",
    #     "ids": {
    #         "y": "GR_aff52c9783a5c3e0c7d92888e4836132e934a"
    #     },
    #     "y": 3
    # }
    # >>> d.history == {"GR_aff52c9783a5c3e0c7d92888e4836132e934a": None}
    # True
    # >>> from ldict import ldict
    # >>> ldict(x=123123, y=88).show(colored=False)
    # {
    #     "id": "8o_7777595727a6a9db6dff36bdeeb4951dbe065",
    #     "ids": {
    #         "x": "zG_fe3f7ea767dcf8dc65d39bfa9f2c07ef023d0",
    #         "y": "BJ_b41cd0efbf48138cf72cc0cd5f888e779cd84"
    #     },
    #     "x": 123123,
    #     "y": 88
    # }
    # >>> print(ldict(y=88, x=123123))  # Original values are order-insensitive.
    # {
    #     "id": "8o_7777595727a6a9db6dff36bdeeb4951dbe065",
    #     "ids": {
    #         "y": "BJ_b41cd0efbf48138cf72cc0cd5f888e779cd84",
    #         "x": "zG_fe3f7ea767dcf8dc65d39bfa9f2c07ef023d0"
    #     },
    #     "y": 88
    #     "x": 123123,
    # }
    # >>> ldict(y=88, x=123123) != ldict(x=88, y=123123)  # Ids of original values embbed the keys.
    # True
    # >>> d = ldict(x=123123, y=88)
    # >>> e = d >> (lambda x: {"z": x**2}) >> (lambda x,y: {"w": x/y})
    # >>> e.show(colored=False)
    # {
    #     "id": "bD9K2iSL5i7-JztWcQ6TbDYzcKTZsuLzkF84sOwe",
    #     "ids": {
    #         "w": "L7FqOGqmIvSqrH8sHGdry3Hp4HQfTbFo4RK7M5M5",
    #         "z": "cyxpRtlCkZvHkalIHQ4PFyrXVsQJBi6bgQpYHIM8",
    #         "x": "zG_fe3f7ea767dcf8dc65d39bfa9f2c07ef023d0",
    #         "y": "BJ_b41cd0efbf48138cf72cc0cd5f888e779cd84"
    #     },
    #     "w": "→(x y)",
    #     "z": "→(x)",
    #     "x": 123123,
    #     "y": 88
    # }
    # >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x,y: {"w": x/y})
    # >>> b = d >> (lambda x,y: {"w": x/y}) >> (lambda x: {"z": x**2})
    # >>> a != b  # Calculated values are order-sensitive.
    # True
    """

    def __init__(self, /, _dictionary=None, identity=ø40, readonly=False, **kwargs):
        self.identity, self.readonly, self.digits, self.version = identity, readonly, identity.digits, identity.version
        self.blobs = {}
        self.hashes = {}
        self.hoshes = {}
        self.hosh = identity
        self.rho = identity.rho
        self.history = {}
        self.last = None
        super().__init__()
        self.data.update(id=identity.id, ids={})
        self.update(**kwargs)

    def __setitem__(self, key: str, value):
        if self.readonly:
            raise Exception(f"Cannot change a readonly ldict ({self.id}).", key)
        if not isinstance(key, str):
            raise Exception(f"Key must be string, not {type(key)}.", key)
        if callable(value):
            raise Exception(f"A value for the field [{key}] cannot have type {type(value)}. "
                            f"For (pseudo)inplace function application, use operator >>= instead")
        if isinstance(value, Ldict):
            value = value.clone(readonly=True)

        if key in self.data:
            del self[key]
        self.blobs[key] = dumps(value, option=OPT_SORT_KEYS)
        self.hashes[key] = self.identity.h * self.blobs[key]
        self.hoshes[key] = self.hashes[key] & key.encode()
        print(11111111111, key, self.blobs[key], self.hashes[key], self.hoshes[key])
        self.hosh *= self.hoshes[key]
        self.data[key] = value
        self.data["id"] = self.hosh.id
        self.data["ids"][key] = self.hoshes[key].id
        extend_history(self, self.hoshes[key])

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise Exception(f"Key must be string, not {type(item)}.", item)
        if item not in self.data:
            raise KeyError(item)
        content = self.data[item]
        if isinstance(content, Lazy):
            self.data[item] = content()
        return self.data[item]

    def __delitem__(self, key):
        if self.readonly:
            raise Exception(f"Cannot change a readonly ldict ({self.id}).", key)
        if not isinstance(key, str):
            raise Exception(f"Key must be string, not {type(key)}.", key)
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
        return self.hosh != other.hosh

    def __getattr__(self, item):
        if item in self:
            return self[item]
        return self.__getattribute__(item)

    def show(self, colored=True):
        """
        >>> from ldict import ldict
        >>> ldict(x=134124, y= 56).show(colored=False)
        {
            "id": "99_942778f763a6e52f8c64e8fc1a7fb7d098bc0",
            "ids": {
                "x": "cv_5254bd1e878c7902da0bc4f66653c307b4a67",
                "y": "YF_6495611adb58599ab1697a11c32cf314c3169"
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
        '{\\n    "id": "99_942778f763a6e52f8c64e8fc1a7fb7d098bc0",\\n    "ids": {\\n        "x": "cv_5254bd1e878c7902da0bc4f66653c307b4a67",\\n        "y": "YF_6495611adb58599ab1697a11c32cf314c3169"\\n    },\\n    "x": 134124,\\n    "y": 56\\n}'
        """
        return self.__repr__(all=True)

    def __rshift__(self, other: Union[Dict, Callable]):
        clone = self.clone()

        # Insertion of dict-like.
        if isinstance(other, Dict):
            for k, v in other.items():
                if v is None:
                    delete(clone, k)
                elif callable(v):
                    raise Exception(f"Value (for field {k}) cannot have type {type(v)}")
                elif k not in ["id", "ids"]:
                    clone[k] = v
                elif k in self.data:
                    raise Exception(f"Cannot overwrite field ({k}) via value insertion through >>")
            return clone
        elif not callable(other):
            raise Exception(f"Function should be callable or dict-like, not {type(other)}")

        # Attach hosh to f if needed.
        if not hasattr(other, "hosh"):
            other.hosh = fhosh(other, version=self.version)
        if other.hosh.etype != "ordered":
            raise FunctionTypeException(f"Functions are not allowed to have etype {other.hosh.etype}.")

        # TODO PartialDict qnd deps nã existem ainda
        input = input_fields(self, other)
        output = output_fields(other)
        u = clone.hosh
        uf = clone.hosh * other.hosh
        ufu_ = uf * ~u

        # Add triggers for future evaluation.
        clone.data = {"id": uf.id, "ids": {}}
        clone.hoshes = {}
        # clone.hashes = {}    atualiza hashes e blobs?
        clone.hosh = uf

        # TODO deduplicate code
        if len(output) == 1:
            field = output[0]
            clone.hoshes[field] = substitute(self.hoshes, [field], uf) if field in self.data else ufu_
            clone.data[field] = Lazy(field, other, deps={k: self.data[k] for k in input})
            clone.data["ids"][field] = clone.hoshes[field].id
        else:
            acc = self.identity
            c = 0
            ufu__ = substitute(self.hoshes, output, uf)
            for i, field in enumerate(output):
                if i < len(output) - 1:
                    field_hosh = ufu__ * (self.digits // 2 * "-" + str(c).rjust(self.digits // 2, "."))
                    c += 1
                    acc *= field_hosh
                else:
                    field_hosh = ~acc * ufu__
                clone.hoshes[field] = field_hosh
                clone.data[field] = Lazy(field, other, deps={k: self.data[k] for k in input})
                clone.data["ids"][field] = field_hosh.id

        for k, v in self.data.items():
            if k not in clone.data:
                clone.data[k] = v
                clone.data["ids"][k] = self.data["ids"][k]
        for k, v in self.hoshes.items():
            if k not in clone.hoshes:
                clone.hoshes[k] = v

        extend_history(clone, clone.hosh)
        return clone
        # TODO: d >> {"x": None}   delete by name
        #   histórico vai ser aumentado em : (---...----x)    e vai placeholder em d
        # TODO: d >> {2: None}   delete by index

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
        obj.history = deepcopy(self.history)
        return obj

    def evaluate(self):
        """
        Usage:

        >>> from ldict import ldict
        >>> a = ldict(x=3) >> (lambda x: {"y": x+2})
        >>> a.show(colored=False)
        {
            "id": "afegcFZ8MTL4Ll30sPbTuTfvpp2yW4AU0sYuSnwe",
            "ids": {
                "y": "02pEMQf2c..XZ4ZlxekIFIAl9u2yW4AU0sYuSnwe",
                "x": "J._041f61a76b07667e8e845c85b397b2a51b620"
            },
            "y": "→(x)",
            "x": 3
        }
        >>> a.evaluate()
        >>> a.show(colored=False)
        {
            "id": "afegcFZ8MTL4Ll30sPbTuTfvpp2yW4AU0sYuSnwe",
            "ids": {
                "y": "02pEMQf2c..XZ4ZlxekIFIAl9u2yW4AU0sYuSnwe",
                "x": "J._041f61a76b07667e8e845c85b397b2a51b620"
            },
            "y": 5,
            "x": 3
        }

        Returns
        -------

        """
        for field in self:
            _ = self[field]

    def _trigger(self, output_field, f, fargs):

        def closure():
            # Process.
            try:
                input_dic = self._getkwargs(fargs)  # evaluate input
                output_dic = f(**input_dic)  # evaluate output
            except MissingField as mf:
                print(self)
                raise MissingField(f"Missing field {mf} needed by {f} to calculate field {output_field}.")

            # Reflect changes.
            for arg, value in output_dic.items():
                self.data[arg] = value

            return self[output_field]

        return closure

    def __xor__(self, f: Union[Dict, Callable]):
        def trigger(output_field):
            def closure():
                # Try loading.
                if output_field in db:
                    return db[output_field]

                # Return requested value without caching, if it has no cost.
                value = self.data[output_field]
                if not isinstance(v, Lazy):
                    return value

                # Process and save (all fields, to avoid a parcial ldict being stored).
                for field in self.ids:
                    db[field] = self[field]

                # Return requested value.
                return self[output_field]

            return closure

        clone = self.copy()
        for field, v in list(self.data.items())[2:]:
            clone.data[field] = trigger(field)
        return clone >> f

    def _getkwargs(self, fargs):
        dic = {}
        for k in fargs:
            if k not in self:
                raise MissingField(k)
            dic[k] = self[k]
        return dic


ldict = Ldict
