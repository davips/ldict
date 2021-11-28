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
from inspect import signature
from types import FunctionType
from typing import Union

from lange import AP, GP

from ldict.core.inspection import (
    extract_dynamic_input,
    extract_output,
    extract_returnstr,
    extract_dictstr,
    extract_body,
)
from ldict.core.inspection import extract_input
from ldict.exception import InconsistentLange, UndefinedSeed, DependenceException
from ldict.lazyval import LazyVal
from ldict.parameter.let import AbstractLet


def handle_dict(data, dictlike, rnd):
    """
    >>> from ldict import ldict
    >>> d = ldict(x=5, y=7, z=8)
    >>> di = handle_dict(d.frozen.data, {"y":None}, None)
    >>> di
    {'x': 5, 'z': 8}
    >>> handle_dict(di, {"w":lambda x,z: x**z}, None)
    {'x': 5, 'z': 8, 'w': →(x z)}
    """
    data = data.copy()
    for k, v in dictlike.items():
        if v is None:
            del data[k]
        else:
            from ldict.core.ldict_ import Ldict

            if callable(v):
                data[k] = lazify(data, k, v, rnd, multi_output=False)
            elif isinstance(v, Ldict):
                data[k] = v.frozen
            else:
                data[k] = v
    return data


def lazify(data, output_field: Union[list, str], f, rnd, multi_output) -> Union[dict, LazyVal]:
    """Create lazy values and handle metafields.
    >>> from ldict import ldict, let
    >>> from random import Random
    >>> (d := ldict(x=5) >> Random(0) >> (lambda x, a=1, b=[1, 2, 3, ... , 8]: {"y": a*x + b, "_parameters": ...}))
    {
        "x": 5,
        "y": "→(a b x)",
        "_parameters": {
            "a": 1,
            "b": 7
        }
    }
    >>> d.y
    12
    >>> d = ldict(x=5) >> Random(0) >> let(
    ...     (lambda x, a=1, b=[1, 2, 3, ... , 8]: {"y": a*x + b, "_parameters": ...}),
    ...     a=3, b=5
    ... )
    >>> d
    {
        "x": 5,
        "y": "→(a b x)",
        "_parameters": {
            "a": 3,
            "b": 5
        }
    }
    >>> d.y
    20
    >>> def f(input="a", output="b", **kwargs):
    ...     return {output: kwargs[input], "_history": ...}
    >>> f.metadata = {"id": "fffffff----------------------------fffff",
    ...             "name": "f",
    ...             "description": "Copy.",
    ...             "code": ...,
    ...             "parameters": ...}
    >>> d = ldict(a=5) >> let(f, output="b")
    >>> d.b
    5
    >>> d
    {
        "a": 5,
        "b": 5,
        "_history": {
            "fffffff----------------------------fffff": {
                "name": "f",
                "description": "Copy.",
                "code": "def f(input='a', output='b', **kwargs):\\nreturn {output: kwargs[input], '_history': ...}",
                "parameters": {
                    "input": "a",
                    "output": "b"
                }
            }
        }
    }
    """
    # TODO (minor): simplify to improve readability of this function
    config, f = (f.config, f.f) if isinstance(f, AbstractLet) else ({}, f)
    if isinstance(f, FunctionType):
        body = extract_body(f)
        memo = [""]

        def lazy_returnstr():
            memo[0] = extract_returnstr("".join(body))
            if multi_output:
                memo[0] = extract_dictstr(memo[0])
            return memo[0]

        dynamic_input = extract_dynamic_input(lazy_returnstr)
    else:
        body = None
        if not (hasattr(f, "metadata") and "input" in f.metadata and "output" in f.metadata):
            raise Exception(f"Missing 'metadata' containing 'input' and 'output' keys for custom callable '{type(f)}'")
        lazy_returnstr = lambda: ""
        dynamic_input = f.metadata["input"]["dynamic"] if "dynamic" in f.metadata["input"] else []

    if not dynamic_input and hasattr(f, "metadata") and "input" in f.metadata and "dynamic" in f.metadata["input"]:
        dynamic_input = f.metadata["input"]["dynamic"]

    input_fields, parameters = extract_input(f)
    for k, v in config.items():
        parameters[k] = v
    for par in dynamic_input:
        if par not in parameters:  # pragma: no cover
            raise Exception(f"Parameter '{par}' value is not available:", parameters)
        input_fields.append(parameters[par])
    deps = prepare_deps(data, input_fields, parameters, rnd)
    for k, v in parameters.items():
        parameters[k] = deps[k]

    newidx = 0
    if hasattr(f, "metadata"):
        step = f.metadata.copy()
        if "id" in step:
            newidx = step.pop("id")
        for k in ["input", "output", "function"]:
            if k in step:
                del step[k]
        if "code" in f.metadata and f.metadata["code"] is ...:
            if body is None:
                raise Exception(f"Cannot autofill 'metadata.code' for custom callable '{type(f)}'")
            head = f"def f{str(signature(f))}:"
            code = head + "\n" + body[0]
            f.metadata["code"] = code
            step["code"] = code
        if "parameters" in f.metadata and f.metadata["parameters"] is ...:
            f.metadata["parameters"] = parameters
            step["parameters"] = parameters
        if "function" in f.metadata and f.metadata["function"] is ...:
            # REMINDER: it is not clear yet whether somebody wants this...
            if hasattr(f, "pickle_dump"):
                f.metadata["function"] = f.pickle_dump
            else:
                import dill

                dump = dill.dumps(f, protocol=5)
                f.metadata["function"] = dump
                f.pickle_dump = dump  # Memoize
    else:
        step = {}

    if output_field == "extract":
        explicit, meta, meta_ellipsed = extract_output(f, lazy_returnstr, deps)
        lazies = []
        dic = {k: LazyVal(k, f, deps, lazies) for k in explicit + meta}
        lazies.extend(dic.values())
        for metaf in meta_ellipsed:
            if metaf == "_code":
                if hasattr(f, "metadata") and "code" in f.metadata:
                    dic["_code"] = f.metadata["code"]
                else:
                    if body is None:
                        raise Exception(f"Missing 'metadata' containing 'code' key for custom callable '{type(f)}'")
                    head = f"def f{str(signature(f))}:"
                    dic["_code"] = head + "\n" + body[0]
            elif metaf == "_parameters":
                dic["_parameters"] = parameters
            elif metaf == "_function":
                # REMINDER: it even more unclear whether somebody wants this...
                if hasattr(f, "pickle_dump"):
                    dic["_function"] = f.pickle_dump
                else:
                    import dill

                    dump = dill.dumps(f, protocol=5)
                    dic["_function"] = dump
                    f.pickle_dump = dump  # Memoize
            elif metaf == "_history":
                if "_history" in data:
                    last = list(data["_history"].keys())[-1]
                    if isinstance(last, int):
                        newidx = last + 1
                    dic["_history"] = data["_history"].copy()
                else:
                    dic["_history"] = {}
                dic["_history"][newidx] = step
            else:
                raise Exception(f"'...' is not defined for '{metaf}'.")
        return dic
    else:
        return LazyVal(output_field, f, deps, None)


def prepare_deps(data, input, parameters, rnd):
    """Build a dict containing all needed dependencies (values) to apply a function:
        input fields and parameters.

    Parameter values are given in let() or sampled according to a range using a random number generator that provides a 'choice' method.
    A range is specified as the default value of the parameter in the function signature.
    """
    deps = {}
    for k, v in parameters.items():
        if isinstance(v, list):
            if rnd is None:  # pragma: no cover
                raise UndefinedSeed(
                    "Missing Random object (or some object with the method 'choice') "
                    "before parameterized function application.\n"
                    "Example: ldict(x=5) >> Random(42) >> (lambda x, a=[1,2,3]: {'y': a * x**2})"
                )
            deps[k] = rnd.choice(expand(v))
        elif v is None:  # pragma: no cover
            raise DependenceException(f"'None' value for parameter '{k}'.", deps.keys())
        else:
            deps[k] = v
    for k in input:
        if k not in data:  # pragma: no cover
            raise DependenceException(f"Missing field '{k}'.", data.keys())
        if data[k] is None:  # pragma: no cover
            raise DependenceException(f"'None' value for field '{k}'.", data.keys())
        deps[k] = data[k]
    return deps


def expand(lst):
    """Evaluate list representing A. or G. progression

    >>> expand([1,2,3,...,9])
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> expand([1,2,4,...,20])
    [1, 2, 4, 8, 16]

    Parameters
    ----------
    lst

    Returns
    -------

    """
    return list(list2progression(lst)) if Ellipsis in lst else lst


def list2progression(lst):
    """Convert list representing A. or G. progression to lange

    >>> list2progression([1,2,3,...,9])
    [1 2 .+. 9]
    >>> list2progression([1,2,4,...,16])
    [1 2 .*. 16]

    Parameters
    ----------
    lst

    Returns
    -------

    """
    # TODO move this to lange package
    try:
        diff1 = lst[1] - lst[0]
        diff2 = lst[2] - lst[1]
        ratio1 = lst[1] / lst[0]
        ratio2 = lst[2] / lst[1]
    except:
        raise InconsistentLange(f"Cannot identify whether this is a G. or A. progression: {lst}")
    newlst = [lst[0], lst[1], ..., lst[-1]]
    if diff1 == diff2:
        return AP(*newlst)
    elif ratio1 == ratio2:
        return GP(*newlst)
    else:
        raise InconsistentLange(f"Cannot identify whether this is a G. or A. progression: {lst}")
