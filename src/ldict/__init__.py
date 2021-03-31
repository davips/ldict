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
from ldict.data import process


class Ldict(Aux, Dict[str, VT]):
    def __init__(self, /, _dictionary=None, keepblob=False, **kwargs) -> None:
        """Uniquely identified lazy dict for serializable pairs str->value
        (serializable in the project 'orjson' sense).
        Usage:
        >>> from ldict import ldict
        >>> print(ldict(X=123123))
        {
            "id": "0000000000000000000007LGxmlWgkN894sZEneXuIp",
            "X": 123123,
            "id_*": "<hidden fields>"
        }
        """
        super().__init__()
        self.data: Dict[str, VT] = {}
        self.hashes, self.blobs = {}, {}
        self.keepblob, self.hash = keepblob, identity
        if _dictionary is not None:
            self.update(_dictionary)  # REMINDER: update() acts on self.data.
        if kwargs:
            self.update(kwargs)

    def __getitem__(self, field: str) -> VT:
        if field in self.data:
            content = self.data[field]
            if callable(content):
                self.data[field] = self.data[field](**self._getargs(field, content))
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
            dic = self._getargs(field, f, fargs)
            self.update(**f(**dic))
            return self[field]

        return closure

    def __setitem__(self, field: str, value: VT) -> None:
        self.data["id"] = None
        self.data[field] = value
        fid = f"id_{field}"
        h = None
        if fid not in self.data:
            h, blob = process(field, value)
            if blob and self.keepblob:
                self.blobs[field] = blob
            self.hashes[field] = h
        self.hash *= self.hashes[field]
        self.data["id"] = self.hash.id
        if h:
            self.data["id_" + field] = h.id

    def __rshift__(self, f):
        """Used for multiple return values, or to avoid inplace update."""
        if not callable(f):
            raise Exception("f should be callable.")

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
            raise Exception("Cannot detect output fields: Missing some structure in the function body.")

        # Detect input fields.
        fargs = signature(f).parameters.keys()

        # Add triggers for future evaluation.
        for k in output_fields:
            self.data[k]= self._trigger(k, f, fargs)

        if f.hash.s==0 and k in self.data:
            raise Exception("Cannot overwrite fields using a function that commutes, i.e. with s=0.")
        return self

    def __delitem__(self, field: str) -> None:
        del self.data[field]
        raise Exception("Not implemented")


ldict = Ldict
