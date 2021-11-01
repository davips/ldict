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

from ldict.exception import NoInputException, NoReturnException, BadOutput, UnderscoreInField, MultipleDicts


def extract_input(f):
    pars = dict(signature(f).parameters)
    input, parameters = [], {}
    if "kwargs" in pars:
        del pars["kwargs"]
    for k, v in pars.items():
        if v.default is v.empty:
            input.append(k)
        else:
            parameters[k] = v.default
    if not input and not parameters:
        raise NoInputException(f"Missing function input parameters.")
    return input, parameters


def extract_returnstr(f):
    """
    >>> def f(x, y, implicit=["a", "b", "c"]):
    ...     return x*y, x+y, x/y
    >>> extract_returnstr(f)
    '(x * y, x + y, x / y)'
    """
    out = StringIO()
    decompile(bytecode_version=(3, 8, 10), co=f.__code__, out=out)
    code = "".join([line for line in out.getvalue().split("\n") if not line.startswith("#")])
    if "return" not in code:
        raise NoReturnException(f"Missing return statement:", code)
    strs = re.findall("(?<=return )(.+)", code)
    if len(strs) != 1:  # pragma: no cover
        raise BadOutput("Cannot detect return expression.", strs)
    return strs[0]


def extract_dictstr(returnstr):
    """
    >>> def f(x, y, implicit=["a", "b", "c"]):
    ...     return {
    ...         "z": x*y,
    ...         "w": x+y,
    ...         implicit: x/y
    ...     }
    >>> extract_dictstr(extract_returnstr(f))
    "{'z': x * y,  'w': x + y,  implicit: x / y}"
    """
    dict_strs = re.findall("(?={)(.+?)(?<=})", returnstr)
    if len(dict_strs) == 0:
        raise BadOutput(
            "Cannot detect output fields, or missing dict (with proper pairs 'identifier'->result) as a return value.",
            dict_strs,
        )
    if len(dict_strs) > 1:
        raise MultipleDicts("Cannot detect output fields, multiple dicts as a return value.", dict_strs)
    return dict_strs[0]


def extract_output(f, dictstr, deps):
    """Extract output fields. They cannot contain underscores.

    https://stackoverflow.com/a/68753149/9681577

    >>> extract_output(lambda:None, "{'z': x*y, 'w': x+y, implicitfield: y**2}", {"implicitfield":"k"})
    ['z', 'w', 'k']
    """
    explicit = re.findall(r"[\"']([a-zA-Z]+[a-zA-Z0-9]*)[\"']:", dictstr)
    implicit = re.findall(r"[ {]([_a-zA-Z]+[_a-zA-Z0-9]*):", dictstr)
    for field in implicit:
        if "_" in field:  # pragma: no cover
            raise UnderscoreInField("Field names cannot contain underscores:", field, dictstr)
        if field not in deps:  # pragma: no cover
            raise Exception("Missing parameter providing implicit field", field, deps)
        explicit.append(deps[field])
    if not explicit:  # pragma: no cover
        pprint(dictstr)
        raise BadOutput("Could not find output fields that are valid identifiers (or kwargs[...]):")
    return explicit


def extract_implicit_input(dictstr):
    return re.findall(r"kwargs\[([a-zA-Z]+[a-zA-Z0-9_]*)][^:]", dictstr)
