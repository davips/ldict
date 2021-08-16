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
from inspect import signature
from io import StringIO
from typing import Dict, Union, Callable

from garoupa import identity32, identity64, Hosh
from uncompyle6.main import decompile

from ldict.abs.mixin.aux import Aux, VT
from ldict.data import process, fhosh


# Dict typing inheritance initially based on https://stackoverflow.com/a/64323140/9681577
# TODO: aceitar qq class que sirva no lugar de Hosh, em vez da string 'version'. Requer Hosh32 e Hosh64 herdando de Hosh
#           serve pra viabilizar teste exaustivo de grupo pequeno pra ver se o artigo funciona
class Ldict_(Aux, Dict[str, VT]):
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
        "id": "yk81NHFkhUQg.3W8CiZjeayh8367tNNSrQu9rVtqkCDHcaaBiju6GMVtyxp.h1Ac",
        "ids": {
            "w": "94Dfzc9y5U0BIYL6NeE-oidtGaA28wYqyASJAV39umabOWr9Iz0PseJTunWMwA8G",
            "z": "pfwOevvOc0THi7b1R4kjIhqtqUgM.-hm1DsEfbPnE4cYsXnffFhkXvSDXzt6mQVV",
            "x": "0000000000000000000001rvYECRwLyX0-V2zUk5HJ.QE5wqO8-0OdDQBV4vkwcE",
            "y": "0000000000000000000002QrIU4K9LkrjRjOxGJlTLXniuT1bLMpZ8glu3j9Te0f"
        },
        "w": "<unevaluated lazy field>",
        "z": "<unevaluated lazy field>",
        "x": 123123,
        "y": 88
    }
    >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x,y: {"w": x/y})
    >>> b = d >> (lambda x,y: {"w": x/y}) >> (lambda x: {"z": x**2})
    >>> a != b  # Calculated values are order-sensitive.
    True
    """

    def __init__(self, /, _dictionary=None, keepblob=False, version="UT64.4", **kwargs) -> None:
        super().__init__()
        if version == "UT32.4":
            self.identity = identity32
            self.rho0 = Hosh.fromid("------------------------------.0", version="UT32.4")
        elif version == "UT64.4":
            self.identity = identity64
            self.rho0 = Hosh.fromid(
                "--------------------------------------------------------------.0", version="UT64.4"
            )
        else:
            raise Exception("Unknown version:", version)

        self.keepblob, self.hosh, self.version = keepblob, self.identity, version
        self.hoshes, self.blobs, self.previous = {}, {}, {}
        self.data: Dict[str, VT] = {"id": self.hosh.id, "ids": {}}  # 'id' will always be the first field
        if _dictionary is not None:
            self.update(_dictionary)  # REMINDER: update() acts on self.data.
        if kwargs:
            self.update(kwargs)

    def __getitem__(self, field: str) -> VT:
        if field in self.data:
            content = self.data[field]
            if callable(content):
                if field in self.previous:
                    self.data[field] = self.previous[field].pop()
                    if len(self.previous[field]) == 0:
                        del self.previous[field]
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
        if not isinstance(field, str):
            raise Exception(f"Key must be string, not {type(field)}.", field)

        # Work around field overwrite.
        if field in self.data:
            if callable(value):
                if field in self.previous:
                    self.previous[field].append(self.data[field])
                else:
                    self.previous[field] = [self.data[field]]
                # TODO: histórico aqui vai ser aumentado em: f
            else:
                del self[field]
                # TODO: histórico aqui vai ser aumentado em: (---...----x)x'

        # Create field's hosh and update ldict's hosh.
        h, blob = process(field, value, version=self.version)
        old_hash = self.hosh
        self.hosh *= h
        field_hash = self.hosh / old_hash if blob is None else h
        self.hoshes[field] = field_hash

        # Update data.
        self.data[field] = value
        self.data["id"] = self.hosh.id
        self.data["ids"][field] = field_hash.id

        # Keep blob if required. TODO: keep hosh sem key embutida
        if blob and self.keepblob:
            self.blobs[field] = blob

    def __delitem__(self, field: str) -> None:
        # REMINDER: esse del não cria placeholder, para ficar intuitivo manipular um dict. põe x, tira x etc.
        #           é distinto da remoção by name/index.
        del self.data[field]
        del self.hoshes[field]
        del self.data["ids"][field]
        self.hosh = self.identity
        for hosh in self.hoshes.values():
            self.hosh *= hosh
        # TODO: histórico aqui vai ser p/ del d[y] : [yzw]-¹zw

    def __rshift__(self, f: Union[Dict, Callable]):
        """Used for multiple return values, or to insert values during a multistep process.
        >>> from ldict import ø
        >>> d = ø >> {"x": 1} >> (lambda x: {"y": x**2}) >> (lambda x,y:{"z": x+y, "w": x/y})
        >>> d.show(colored=False)
        {
            "id": "QNRxg0I5naPZX-dls7VQ622Htt-Q1Yfx2IL1DiJH0EtihD-yzK8y1qb7KysmVigM",
            "ids": {
                "z": "scVKB6ugOhLvjEhlIt4JPhWJl1qTZB1Y4SbQIOy55UbEm2bEumU8bfRktf0ZDWCc",
                "w": "111111110GZ11111114bRi9Np1yhkc31s9Trh6HU.4cocBk71K00FEal5z-gv8Db",
                "y": "nzWNFVcPAeftDkW-KFMU9VXfh1B1uyzVMcIhuAtpHkIsu4i3VaYOlUd8hgCK7TjI",
                "x": "0000000000000000000004nMDSf.TnQ5bqaZyLaOm1jkIt.q0Kxrj1aVGPmDOeqb"
            },
            "z": "<unevaluated lazy field>",
            "w": "<unevaluated lazy field>",
            "y": "<unevaluated lazy field>",
            "x": 1
        }
        """
        # TODO: d >> {"x": None}   delete by name
        #   histórico vai ser aumentado em : (---...----x)    e vai placeholder em d
        # TODO: d >> {2: None}   delete by index
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
        ret = "".join([line for line in out.getvalue().split("\n") if not line.startswith("#")])
        if "return" not in ret:
            print(ret)
            raise Exception(f"Missing return statement:")
        dicts = re.findall("(?={)(.+?)(?<=})", ret)
        if len(dicts) != 1:
            raise Exception(
                "Cannot detect output fields:" "Missing dict (with pairs 'identifier'->result) as a return value.",
                dicts,
                ret,
            )
        output_fields = re.findall(r"(?:[\"'])([a-zA-Z]+[a-zA-Z0-9_]*)(?:[\"'])", dicts[0])

        # Work around field overwrite.
        for field in output_fields:
            if field in clone.data:
                clone.previous[field] = clone.data[field]

        # Detect input fields.
        fargs = signature(f).parameters.keys()

        # Attach hosh to f if needed.
        if not hasattr(f, "hosh"):
            f.hosh = fhosh(f, version=self.version)

        # Update clone id.
        if f.hosh.etype != "ordered":
            raise OverwriteException("Function element probably will never be allowed to have etype!=ordered.")
        old_hash = clone.hosh
        clone.hosh *= f.hosh
        clone.data["id"] = clone.id
        ufu = clone.hosh * ~old_hash  # z = ufu-¹

        # Add triggers for future evaluation.
        acc = self.identity
        new_hashes = {}
        new_data = {"id": clone.id, "ids": {}}
        for i, field in enumerate(output_fields):
            if len(output_fields) == 1:
                field_hash = ufu
            else:
                if i < len(output_fields) - 1:
                    field_hash = ufu * (self.rho0 + Hosh.fromn(i, self.version))
                    acc *= field_hash
                else:
                    field_hash = ~acc * ufu
            new_hashes[field] = field_hash
            # noinspection PyProtectedMember
            new_data[field] = clone._trigger(field, f, fargs)
            new_data["ids"][field] = field_hash.id

        new_hashes.update(clone.hoshes)
        new_data["ids"].update(clone.data["ids"])
        del clone.data["ids"]
        new_data.update(clone.data)

        clone.hoshes = new_hashes
        clone.data = new_data
        return clone


class OverwriteException(Exception):
    pass
