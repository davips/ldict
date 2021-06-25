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

# Dict typing inheritance initially based on https://stackoverflow.com/a/64323140/9681577
import re
from inspect import signature, getsourcelines
from typing import Dict

from garoupa.hash import identity

from ldict.abs.mixin.aux import Aux, VT
from ldict.data import process, fhash


class Ldict(Aux, Dict[str, VT]):
    def __init__(self, /, _dictionary=None, keepblob=False, **kwargs) -> None:
        """Uniquely identified lazy dict for serializable pairs str->value
        (serializable in the project 'orjson' sense).
        Usage:
        >>> from ldict import ldict
        >>> print(ldict(X=123123))
        {
            "id": "1qQTqcJj9iEQB5aNnfviRk55kDEVyiOmrgDEdchosCW",
            "X": 123123,
            "id_X": "<hidden field>"
        }
        """
        super().__init__()
        self.keepblob, self.hash = keepblob, identity
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
        h, blob = process(field, value)
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

    def __rshift__(self, f):
        """Used for multiple return values, or to avoid inplace update of the ldict."""
        clone = self.copy()
        if isinstance(f, dict):
            for k, v in f.items():
                clone[k] = v
            return clone
        elif not callable(f):
            raise Exception("f should be callable or dict.")

        # Extract output fields.
        lines = getsourcelines(f)[0]
        returns = [line for line in lines if "return" in line]
        if len(returns) != 1:
            if "lambda" not in lines[0]:
                raise Exception(f"A single 'return <dict>' statement is expected. Not {len(returns)} occurrences."
                                f"Lambdas should be inline.")
            returns = [lines[0]]
        rx = r"(?:[\"'])([a-zA-Z]+[a-zA-Z0-9_]*)(?:[\"'])"
        output_fields = re.findall(rx, returns[0])
        if not output_fields:
            raise Exception("Cannot detect output fields: Missing dict as return value.")

        # Work around field overwrite.
        for field in output_fields:
            if field in clone.data:
                clone.previous[field] = clone.data[field]

        # Detect input fields.
        fargs = signature(f).parameters.keys()

        # Attach hash to f if needed.
        if not hasattr(f, "hash"):
            f.hash = fhash(f)

        # Add triggers for future evaluation.
        for field in output_fields:
            if f.hash.s == 0 and field in clone.data:
                raise OverwriteException("Cannot overwrite fields using a function that commutes, i.e. with s=0.")
            old_hash = clone.hash
            clone.hash *= f.hash
            field_hash = clone.hash / old_hash
            clone.hashes[field] = field_hash
            clone.data[field] = clone._trigger(field, f, fargs)
            clone.data["id"] = clone.hash.id
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


ldict = Ldict


class OverwriteException(Exception):
    pass
