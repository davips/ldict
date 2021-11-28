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

from ldict.exception import NoInputException, NoReturnException, BadOutput, MultipleDicts


def extract_input(f):
    """
    >>> f = lambda x, y, z=5: None
    >>> extract_input(f)
    (['x', 'y'], {'z': 5})
    >>> f.metadata = {"input": {"fields": ["a", "b"], "parameters": {"c": 7}}}
    >>> extract_input(f)
    (['a', 'b'], {'c': 7})
    """
    if hasattr(f, "metadata") and "input" in f.metadata:
        fields = f.metadata["input"]["fields"] if "fields" in f.metadata["input"] else []
        hasparams = "parameters" in f.metadata["input"] and f.metadata["input"]["parameters"] is not ...
        parameters = f.metadata["input"]["parameters"] if hasparams else {}
        return fields, parameters
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


def extract_body(f):
    """
    >>> def f(x, y, implicit=["a", "b", "c"]):
    ...     return x*y, x+y, x/y
    >>> extract_body(f)
    ['return (x * y, x + y, x / y)']
    """
    if hasattr(f, "metadata") and "code" in f.metadata and f.metadata["code"] is not ...:
        return f.metadata["code"]
    out = StringIO()
    decompile(bytecode_version=(3, 8, 10), co=f.__code__, out=out)
    code = [line for line in out.getvalue().split("\n") if not line.startswith("#")]
    return code or None


def extract_returnstr(code) -> str:
    """
    >>> def f(x, y, implicit=["a", "b", "c"]):
    ...     return x*y, x+y, x/y
    >>> extract_returnstr("".join(extract_body(f)))
    '(x * y, x + y, x / y)'
    """
    if "return" not in code:
        raise NoReturnException(f"Missing return statement:", code)
    strs = re.findall("(?<=return )(.+)", code)
    if len(strs) != 1:  # pragma: no cover
        raise BadOutput("Cannot detect return expression.", strs)
    return strs[0]


def extract_dictstr(returnstr: str) -> str:
    """
    >>> def f(x, y, implicit=["a", "b", "c"]):
    ...     return {
    ...         "z": x*y,
    ...         "w": x+y,
    ...         implicit: x/y
    ...     }
    >>> extract_dictstr(extract_returnstr("".join(extract_body(f))))
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


def extract_output(f, lazy_dictstr, deps):
    """Extract output fields.

    https://stackoverflow.com/a/68753149/9681577

    >>> extract_output(lambda:None, lambda:"{'z': x*y, 'w': x+y, implicitfield: y**2, '_history': ..., '_code': ..., '_metafield2': 'some text'}", {"implicitfield": "k"})
    (['z', 'w', 'k'], ['_metafield2'], ['_history', '_code'])
    """
    metadata_output = f.metadata["output"] if hasattr(f, "metadata") and "output" in f.metadata else {}
    if "fields" in metadata_output:
        explicit = f.metadata["output"]["fields"]
    else:
        explicit = re.findall(r"[\"']([a-zA-Z]+[_a-zA-Z0-9]*)[\"']:", lazy_dictstr())
    if "auto" in metadata_output:
        meta_ellipsed = f.metadata["output"]["auto"]
    else:
        meta_ellipsed = re.findall(r"[\"'](_[_a-zA-Z]+[_a-zA-Z0-9]*)[\"']:[ ]*?\.\.\.[,}]", lazy_dictstr())
        meta_ellipsed.extend(re.findall(r"[\"'](_[_a-zA-Z]+[_a-zA-Z0-9]*)[\"']:[ ]*?Ellipsis[,}]", lazy_dictstr()))
    if "meta" in metadata_output:
        meta = f.metadata["output"]["meta"]
    else:
        meta = re.findall(r"[\"'](_[_a-zA-Z]+[_a-zA-Z0-9]*)[\"']:", lazy_dictstr())
        meta = [item for item in meta if item not in meta_ellipsed]
    if "dynamic" in metadata_output:
        dynamic = f.metadata["output"]["dynamic"]
    else:
        # REMINDER: identify output that comes as a variable; it will be used to check whether we can detect its content
        # The variable brings the field name.
        dynamic = re.findall(r"[ {]([_a-zA-Z]+[_a-zA-Z0-9]*):", lazy_dictstr())

    for field in dynamic:
        # if "_" in field:  # pragma: no cover
        #     raise UnderscoreInField("Field names cannot contain underscores:", field, dictstr)
        if field not in deps:  # pragma: no cover
            raise Exception("Missing parameter providing implicit field", field, deps)
        explicit.append(deps[field])
    if not explicit:  # pragma: no cover
        pprint(lazy_dictstr())
        raise BadOutput("Could not find output fields that are valid identifiers (or kwargs[...]):")
    return explicit, meta, meta_ellipsed


def extract_dynamic_input(lazy_dictstr):
    """The variable brings the field name, so we can get the field content from kwargs."""
    return re.findall(r"kwargs\[([a-zA-Z]+[a-zA-Z0-9_]*)][^:]", lazy_dictstr())
