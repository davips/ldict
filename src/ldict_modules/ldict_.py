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
#

import re
from inspect import signature
from io import StringIO
from typing import Dict, Union, Callable

from garoupa import identity32, identity64, Hosh
from uncompyle6.main import decompile

from ldict_modules.abs.mixin.aux import Aux, VT
from ldict_modules.data import process, fhosh
# Dict typing inheritance initially based on https://stackoverflow.com/a/64323140/9681577
# TODO: aceitar qq class que tenha id e seja operavel, como valor opcional de 'version'
#           serve pra viabilizar teste exaustivo de grupo pequeno pra ver se o artigo funciona
from ldict_modules.exception import NoInputException, DependenceException, FunctionTypeException, MissingField

db = {}


class Ldict(Aux, Dict[str, VT]):
    """Uniquely identified lazy dict for serializable pairs str->value
    (serializable in the project 'orjson' sense).

    Usage:

    >>> from ldict import ldict
    >>> print(ldict(x=123123, y=88))
    {
        "id": "00000000001R43.FjBZ0mYLLlJ.N9IIz",
        "ids": "<1 hidden ids>",
        "x": 123123,
        "y": 88
    }
    >>> print(ldict(y=88, x=123123))  # Original values are order-insensitive.
    {
        "id": "00000000001R43.FjBZ0mYLLlJ.N9IIz",
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
        "id": "cv8OZU-2XiiYE8wINjteRg7b1kmqDLEQ",
        "ids": {
            "w": "6eLEvjtht1ozfCz6iZGbnGlTN6lxc3P4",
            "z": "6gpauRwNufnwBd-v8N2asyxtJkj7mDmg",
            "x": "00000000003owEf6BiKVZQPmQxLq-IR9",
            "y": "00000000002szrMfKje6X7YowN4ma..D"
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

    def __init__(self, /, _dictionary=None, keepblob=False, version="UT32.4", **kwargs) -> None:
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
                try:
                    self.data[field] = content(**self._getkwargs(signature(content).parameters.keys()))
                except MissingField as mf:
                    print(self)
                    raise MissingField(f"Missing field {mf} to calculate field {field}.")
                return self.data[field]
            else:
                return self.data[field]
        raise KeyError(field)

    def _getkwargs(self, fargs):
        dic = {}
        for k in fargs:
            if k not in self:
                raise MissingField(k)
            dic[k] = self[k]
        return dic

    def __setitem__(self, field: str, value: VT) -> None:
        if not isinstance(field, str):
            raise Exception(f"Key must be string, not {type(field)}.", field)
        if callable(value):
            raise Exception(f"A value for the field [{field}] cannot have type {type(value)}. "
                            f"For inplace function application, use operator >>= instead")

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

        # Keep blob if required. TODO: keep hoshes sem key embutida
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

    def __irshift__(self, f: Union[Dict, Callable]):
        self.__rshift__(f, inplace=True)  # TODO: nunca testado!

    def __rshift__(self, f: Union[Dict, Callable], inplace=False):
        """Used for multiple return values, or to insert values during a multistep process.
        >>> from ldict import ø
        >>> d = ø >> {"x": 1} >> (lambda x: {"y": x**2}) >> (lambda x,y:{"z": x+y, "w": x/y})
        >>> d.show(colored=False)
        {
            "id": "fCbv8nJkRvfb.lKm0hw5oZbEOJFXDCC2",
            "ids": {
                "z": "0o-CIUOcXzxEJqyvxULMntNOme8sg1Xo",
                "w": "1110VN111mYpaXqcmrQu0IuXZ9ztseeR",
                "y": "ecbTxZW6Uzjl2XbK2NvfZVjnF5k82oun",
                "x": "00000000002SznfcfC6QP5WfCU8QuITi"
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
        clone = self if inplace else self.copy()
        # TODO
        #   ...xvwf = ...x'vw
        #   x' = xvf[vw]-¹

        # Insertion of dict.
        if isinstance(f, Dict):
            for k, v in f.items():
                if k not in ["id", "ids"]:
                    clone[k] = v
            return clone
        elif not callable(f):
            raise Exception(f"f should be callable or dict, not {type(f)}")

        # Extract output fields. https://stackoverflow.com/a/68753149/9681577
        if hasattr(f, "output_fields"):
            output_fields = f.output_fields
        else:
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
                clone.previous[field] = [clone.data[field]]

        # Detect input fields.
        if hasattr(f, "input_fields"):
            fargs = f.input_fields
        else:
            fargs = signature(f).parameters.keys()
            if not fargs:
                raise NoInputException(f"Missing function input parameters.")
            for field in fargs:
                if field not in self.data:
                    # TODO: stacktrace para apontar toda a cadeia de dependências, caso seja profunda
                    raise DependenceException(f"Function depends on inexistent field [{field}].")

        # Attach hosh to f if needed.
        if not hasattr(f, "hosh"):
            f.hosh = fhosh(f, version=self.version)

        # Update clone id.
        if f.hosh.etype != "ordered":
            raise FunctionTypeException(f"Functions are not allowed to have etype {f.hosh.etype}.")
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
                if not callable(value):
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
