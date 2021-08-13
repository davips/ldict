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
#  Relevant employers or funding agencies will be notified accordingly.

import re
from inspect import signature, getsourcelines
from io import StringIO
from typing import Dict, Union, Callable

from garoupa.hash import identity32, identity64, Hash
from uncompyle6.main import decompile

from ldict.abs.mixin.aux import Aux, VT
from ldict.data import process, fhash


# Dict typing inheritance initially based on https://stackoverflow.com/a/64323140/9681577
class Ldict(Aux, Dict[str, VT]):
    def __init__(self, /, _dictionary=None, keepblob=False, version="UT64.4", **kwargs) -> None:
        """Uniquely identified lazy dict for serializable pairs str->value
        (serializable in the project 'orjson' sense).
        Usage:
        >>> from ldict import ldict
        >>> print(ldict(x=123123, y=88))
        {
            "id": "0000000000000000000004fXFwHzGuTlkQcR5z1rzEXbWAnrZUJOq5Ua3YnFcvvx",
            "ids": "<1 hidden ids>",
            "x": 123123,
            "y": 88
        }
        >>> print(ldict(y=88, x=123123))  # Original values are order-insensitive.
        {
            "id": "0000000000000000000004fXFwHzGuTlkQcR5z1rzEXbWAnrZUJOq5Ua3YnFcvvx",
            "ids": "<1 hidden ids>",
            "y": 88,
            "x": 123123
        }
        >>> ldict(y=88, x=123123) != ldict(x=88, y=123123)  # Ids of original values embbed the keys.
        True
        >>> d = ldict(x=123123, y=88)
        >>> e = d >> (lambda x: {"z": x**2}) >> (lambda x,y: {"w": x/y})
        >>> e.show(colored=False)
        {
            "id": "vgW1BDwNOaRUw6flbMDjOHcXR..xlXpYYGfdjXjJgD.A1r5kanmtixMWvSuIuHZd",
            "ids": {
                "x": "0000000000000000000001rvYECRwLyX0-V2zUk5HJ.QE5wqO8-0OdDQBV4vkwcE",
                "y": "0000000000000000000002QrIU4K9LkrjRjOxGJlTLXniuT1bLMpZ8glu3j9Te0f",
                "z": "qf-xSZcL2bFnXo1vfmYckQZ3aX7gVACDyZrBYDvh4MNQ1LMiJJLPgMmbdJcP0-PV",
                "w": "111111110GZ11111114bRi9Np1yhkc31s9Trh6HU.4cocBk71K00FEal5z-gv8Db"
            },
            "x": 123123,
            "y": 88,
            "z": "<unevaluated lazy field>",
            "w": "<unevaluated lazy field>"
        }
        >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x,y: {"w": x/y})
        >>> b = d >> (lambda x,y: {"w": x/y}) >> (lambda x: {"z": x**2})
        >>> a != b  # Calculated values are order-sensitive.
        True
        """
        super().__init__()
        if version == "UT32.4":
            self.identity = identity32
            self.rho0 = Hash.fromid("------------------------------.0", version="UT32.4")
        elif version == "UT64.4":
            self.identity = identity64
            self.rho0 = Hash.fromid("--------------------------------------------------------------.0",
                                    version="UT64.4")
        else:
            raise Exception("Unknown version:", version)

        self.keepblob, self.hash, self.version = keepblob, self.identity, version
        self.hashes, self.blobs, self.previous = {}, {}, {}
        self.data: Dict[str, VT] = {"id": self.hash.id, "ids": {}}  # 'id' will always be the first field
        if _dictionary is not None:
            self.update(_dictionary)  # REMINDER: update() acts on self.data.
        if kwargs:
            self.update(kwargs)

    def __getitem__(self, field: str) -> VT:
        if field in self.data:
            content = self.data[field]
            if callable(content):
                if field in self.previous:
                    self.data[field] = self.previous.pop(field)
                print(field, self.previous)
                self.data[field] = content(**self._getargs(field, content))
                return self.data[field]
            else:
                return self.data[field]
        raise KeyError(field)

    def _getargs(self, field, f, fargs=None):
        fargs = fargs or signature(f).parameters.keys()
        dic = {}
        for k in fargs:
            if k not in self:
                print(self)
                raise Exception(f"Missing field {k} needed by {f} to calculate field {field}.")
            dic[k] = self[k]
        return dic

    def _trigger(self, field, f, fargs):
        def closure():
            dic = f(**self._getargs(field, f, fargs))
            for arg, value in dic.items():
                self.data[arg] = value
            return self[field]

        return closure

    def __setitem__(self, field: str, value: VT) -> None:
        # Work around field overwrite.
        if field in self.data and callable(value):
            self.previous[field] = self.data[field]

        # Create field hash and update ldict hash.
        h, blob = process(field, value, version=self.version)
        old_hash = self.hash
        self.hash *= h
        field_hash = self.hash / old_hash
        self.hashes[field] = field_hash

        # Update data.
        self.data[field] = value
        self.data["id"] = self.hash.id
        self.data["ids"][field] = field_hash.id

        # Keep blob if required.
        if blob and self.keepblob:
            self.blobs[field] = blob

    def __rshift__(self, f: Union[Dict, Callable]):
        """Used for multiple return values, or to insert values during a multistep process.
        >>> from ldict import ø
        >>> d = ø >> {"x": 1, "y": 2} >> (lambda x,y: {"z": x+y})  #>> (lambda x,y:{"z": x+y})
        >>> d.show()

        """
        clone = self.copy()
        if isinstance(f, dict):
            for k, v in f.items():
                clone[k] = v
            return clone
        elif not callable(f):
            raise Exception("f should be callable or dict.")

        # Extract output fields. https://stackoverflow.com/a/68753149/9681577
        out = StringIO()
        decompile(bytecode_version=None, co=f.__code__, out=out)
        ret = out.getvalue()
        if "return" not in ret:
                raise Exception(f"Missing return statement:",ret)
        dicts = re.findall(r"(?:[\"'])([a-zA-Z]+[a-zA-Z0-9_]*)(?:[\"'])", ret)
        if len(dicts) != 1:
            raise Exception("Cannot detect output fields:"
                            "Missing dict (with pairs 'identifier'->result) as a return value.", dicts)
        output_fields = dicts[0]

        # Work around field overwrite.
        for field in output_fields:
            if field in clone.data:
                clone.previous[field] = clone.data[field]

        # Detect input fields.
        fargs = signature(f).parameters.keys()

        # Attach hash to f if needed.
        if not hasattr(f, "hash"):
            f.hash = fhash(f, version=self.version)

        print(f.hash)

        # Update clone id.
        if f.hash.etype != "ordered":
            raise OverwriteException("Function probably will never be allowed to have etype!=ordered.")
        old_hash = clone.hash
        clone.hash *= f.hash
        clone.data["id"] = clone.hash.id
        ufu = clone.hash * ~old_hash  # z = ufu-¹

        # Add triggers for future evaluation.
        acc = self.identity
        for i, field in enumerate(output_fields):
            if len(output_fields) == 1:
                field_hash = ufu
            else:
                if i < len(output_fields) - 1:
                    field_hash = ufu * (self.rho0 + Hash.fromn(i, self.version))
                    acc += field_hash
                else:
                    field_hash = ~acc * ufu
            clone.hashes[field] = field_hash
            clone.data[field] = clone._trigger(field, f, fargs)
            clone.data["ids"][field] = field_hash.id

        return clone

    def __delitem__(self, field: str) -> None:
        field_hash = self.hashes[field]
        if field_hash.s == 0:
            raise Exception("Cannot delete an unchanged field (commutative field)."
                            "It would seem like it never existed."
                            "TODO: allow unchanged to be deleted if it was never used"
                            "in the generation of other fields.")

        del self.data[field]
        del self.hashes[field]
        del self.data["ids"][field]
        self.hash /= field_hash


class OverwriteException(Exception):
    pass
