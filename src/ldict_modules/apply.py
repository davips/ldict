#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the garoupa project.
#  Please respect the license - more about this in the section (*) below.
#
#  garoupa is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  garoupa is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with garoupa.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.
import re
from inspect import signature
from io import StringIO
from typing import Callable

from uncompyle6.main import decompile

from ldict_modules.data import fhosh, removal_id
from ldict_modules.exception import NoInputException, DependenceException, FunctionTypeException
from ldict_modules.history import extend_history
from ldict_modules.lazy import Lazy


def delete(d, clone, k):
    """
    >>> from ldict import ø
    >>> d = ø >> {"x": 5, "y": 7}
    >>> d.show(colored=False)
    {
        "id": "I0_39c94b4dfbc7a8579ca1304eba25917204a5e",
        "ids": {
            "x": "Tz_d158c49297834fad67e6de7cdba3ea368aae4",
            "y": "Rs_92162dea64a7462725cac7dcee71b67669f69"
        },
        "x": 5,
        "y": 7
    }
    >>> d >>= {"x": None}  # Delete content by key
    >>> d.show(colored=False)
    {
        "id": "orh.lboHQhzNnrjrircOoPYzfk0000000000000y",
        "ids": {
            "x": "7jItH06N6TKPQ2ikAXqnlk38S69000000000000y",
            "y": "Rs_92162dea64a7462725cac7dcee71b67669f69"
        },
        "x": null,
        "y": 7
    }
    >>> d.history
    {'I0_39c94b4dfbc7a8579ca1304eba25917204a5e': {'Tz_d158c49297834fad67e6de7cdba3ea368aae4', 'Rs_92162dea64a7462725cac7dcee71b67669f69'}, '--------------------...................x': None}

    Parameters
    ----------
    d
    clone
    k

    Returns
    -------

    """

    def f(**kwargs):
        return {k: None}

    f.hosh = d.identity * removal_id(d, k)
    f.input_fields = f.output_fields = [k]
    application(d, clone, f)
    _ = clone[k]


def input_fields(d, f):
    """Extract input fields.

    >>> input_fields(lambda x,y: {"z": x*y, "w": x+y})
    ['z', 'w']
    >>> def f(x,y):
    ...     return {
    ...         "z": x*y,
    ...         "w": x+y
    ...     }
    >>> output_fields(f)
    ['z', 'w']

    Returns
    -------

    """
    input_fields = f.input_fields if hasattr(f, "input_fields") else signature(f).parameters.keys()
    if not input_fields:
        raise NoInputException(f"Missing function input parameters.")
    for field in input_fields:
        if field not in d.data:
            # TODO: stacktrace para apontar toda a cadeia de dependências, caso seja profunda
            raise DependenceException(f"Function depends on inexistent field [{field}].", d.data.keys())
    return input_fields


def output_fields(f):
    """Extract output fields.

    https://stackoverflow.com/a/68753149/9681577

    >>> output_fields(lambda x,y: {"z": x*y, "w": x+y})
    ['z', 'w']
    >>> def f(x,y):
    ...     return {
    ...         "z": x*y,
    ...         "w": x+y
    ...     }
    >>> output_fields(f)
    ['z', 'w']

    Returns
    -------

    """
    if hasattr(f, "output_fields"):
        return f.output_fields
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
    return re.findall(r"(?:[\"'])([a-zA-Z]+[a-zA-Z0-9_]*)(?:[\"'])", dicts[0])


def substitute(hoshes, fields, uf):
    """
    >>> from ldict import ldict
    >>> a = ldict(x=3)
    >>> a.show(colored=False)
    {
        "id": "J._041f61a76b07667e8e845c85b397b2a51b620",
        "ids": {
            "x": "J._041f61a76b07667e8e845c85b397b2a51b620"
        },
        "x": 3
    }
    >>> a >>= (lambda x: {"x": x+2})
    >>> a.show(colored=False)
    {
        "id": "dSe.tHYFkzcOvIRexYWCR5X1drIYDDRQkGiQ6qJ8",
        "ids": {
            "x": "dSe.tHYFkzcOvIRexYWCR5X1drIYDDRQkGiQ6qJ8"
        },
        "x": "→(x)"
    }
    >>> a = ldict(x=3, y=5) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["y"]
    True
    >>> a = ldict(w=2, x=3) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["w"]
    True
    >>> a = ldict(w=2, x=3, z=1, y=4) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["w"] * a.hoshes["z"] * a.hoshes["y"]
    True
    >>> a = ldict(w=2, x=3, z=1, y=4) >> (lambda w,x,y: {"x": x+2, "a": w*x*y})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["a"] * a.hoshes["w"] * a.hoshes["z"] * a.hoshes["y"]
    True
    >>> a = ldict(w=2, x=3, z=1, y=4) >> (lambda w,x,y: {"x": x+2, "y": w*x*y})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["y"] * a.hoshes["w"] * a.hoshes["z"]
    True
    >>> a.show(colored=False)
    {
        "id": "KK4hVq3NIY9hsgeQ51OBFEYwl0FzkEFdqK4B1zjh",
        "ids": {
            "x": "XWni1iw0n1skP35E5GaJXbQuBWAgmEFdqG4B1zji",
            "y": "ofEb.nRSYsUsgAnnyp4KYFovZaUOV6000sv....-",
            "w": "Vz_fe081095fa0e83d34dedead1670ac4d038c83",
            "z": "KY_1ab63deadd6f558588341334641a142ae5867"
        },
        "x": "→(w x y)",
        "y": "→(w x y)",
        "w": 2,
        "z": 1
    }

    Parameters
    ----------
    uf
    hoshes
    fields

    Returns
    -------

    """
    others = uf.ø
    for k, v in hoshes.items():
        if k not in fields:
            others *= v
    return uf * ~others


def application(self, clone, other: Callable):
    # Attach hosh to f if needed.
    if not hasattr(other, "hosh"):
        other.hosh = fhosh(other, version=self.version)
    if other.hosh.etype != "ordered":
        raise FunctionTypeException(f"Functions are not allowed to have etype {other.hosh.etype}.")

    # TODO criar PartialDict qnd deps não existem ainda
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

    extend_history(clone, other.hosh)
