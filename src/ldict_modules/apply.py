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

from uncompyle6.main import decompile

from ldict_modules.exception import NoInputException, DependenceException


def delete(clone, k):
    pass


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
