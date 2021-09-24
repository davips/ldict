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
import re
from inspect import signature
from io import StringIO
from pprint import pprint

from uncompyle6.main import decompile

from ldict.data import fhosh
from ldict.exception import NoInputException, DependenceException, NoReturnException, BadOutput, UnderscoreInField, \
    MultipleDicts, FunctionETypeException


def input_fields(f, previous_fields, identity):
    """Extract input fields (and parameters/hosh, when default values are present).

    >>> from garoupa import ø40
    >>> from ldict.appearance import decolorize
    >>> decolorize(str(input_fields(lambda x,y: {"z": x*y, "w": x+y}, {"x":None, "y":None}, ø40)))
    "(['x', 'y'], {}, vqpiPPzpfpDvaE4UbHnVw3tvx3QmsRaiF9yEw.z7)"
    >>> def f(x, y, a=[1,2,3,...,10], b=[1,2,4,...,32], _id=b"some unique content"):
    ...     return {
    ...         "z": a*x + b*y,
    ...         "w": x+y
    ...     }
    >>> input_fields(f, {"x":None, "y":None}, ø40)[:2]
    (['x', 'y'], {'a': [1, 2, 3, Ellipsis, 10], 'b': [1, 2, 4, Ellipsis, 32]})

    Returns
    -------
    (input, input_fields, hosh)
    """
    parameters = {}
    hosh = identity
    if hasattr(f, "hosh"):
        input = f.input_fields
        hosh *= f.hosh
        if hasattr(f, "parameters"):
            parameters = f.parameters
    else:
        pars = dict(signature(f).parameters)
        input = []
        if "kwargs" in pars:
            del pars["kwargs"]
        for k, v in pars.items():
            if v.default is v.empty:
                input.append(k)
            elif k == "_id":
                hosh *= v.default
            else:
                parameters[k] = v.default
    if not input and not parameters:
        raise NoInputException(f"Missing function input parameters.")
    for field in input:
        if field not in previous_fields:
            # TODO: stacktrace para apontar toda a cadeia de dependências, caso seja profunda
            raise DependenceException(f"Function depends on inexistent field [{field}]. Current",
                                      list(previous_fields.keys())[2:])
    if hosh == identity:
        hosh = fhosh(f, version=identity.version)
    if hosh.etype != "ordered":
        raise FunctionETypeException(f"Function hosh etype ({hosh.etype}) should be 'ordered'.", hosh)
    return input, parameters, hosh


def extract_dicts(f):
    """
    >>> def f(x, y, implicit=["a", "b", "c"]):
    ...     return {
    ...         "z": x*y,
    ...         "w": x+y,
    ...         implicit: x/y
    ...     }
    >>> extract_dicts(f)
    ["{'z': x * y,  'w': x + y,  implicit: x / y}"]
    """
    out = StringIO()
    decompile(bytecode_version=None, co=f.__code__, out=out)
    code = "".join([line for line in out.getvalue().split("\n") if not line.startswith("#")])
    if "return" not in code:
        raise NoReturnException(f"Missing return statement:", code)
    dicts = re.findall("(?={)(.+?)(?<=})", code)
    if len(dicts) != 1:
        raise BadOutput(
            "Cannot detect output fields, or missing dict (with proper pairs 'identifier'->result) as a return value.",
            dicts
        )
    return dicts


def output_fields(f, dicts, parameters):
    """Extract output fields. They cannot contain underscores.

    https://stackoverflow.com/a/68753149/9681577

    >>> output_fields(lambda:None, ["{'z': x*y, 'w': x+y, implicitfield: y**2}"], {"implicitfield":"k"})
    ['z', 'w', 'k']
    """
    if hasattr(f, "output_fields"):
        return f.output_fields, []
    if len(dicts) != 1:
        raise MultipleDicts("Cannot return less or more than one dict:", dicts)

    explicit = re.findall(r"[\"']([a-zA-Z]+[a-zA-Z0-9]*)[\"']:", dicts[0])
    implicit = re.findall(r"[ {]([_a-zA-Z]+[_a-zA-Z0-9]*):", dicts[0])
    for field in implicit:
        if "_" in field:  # pragma: no cover
            raise UnderscoreInField("Field names cannot contain underscores:", field, dicts[0])
        if field not in parameters:
            raise Exception("Missing parameter providing implicit field", field, parameters)
        explicit.append(parameters[field])
    if not explicit:
        pprint(dicts)
        raise BadOutput("Could not find output fields that are valid identifiers (or kwargs[...]):")
    return explicit


def implicit_input(f, dicts, parameters):
    if hasattr(f, "input_fields"):
        return []
    return re.findall(r"kwargs\[([a-zA-Z]+[a-zA-Z0-9_]*)][^:]", dicts[0])
