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

from typing import Callable, Union

from lange import AP, GP

from ldict.core.inspection import extract_dictstr, extract_implicit_input, extract_output
from ldict.core.inspection import extract_input
from ldict.exception import InconsistentLange
from ldict.lazyval import LazyVal


def handle_dict(data, dictlike, rnd):
    """
    >>> from ldict.frozenlazydict import FrozenLazyDict as ldict
    >>> d = ldict(x=5, y=7, z=8)
    >>> handle_dict(d, {"y":None})
    >>> d
    {
        "x": 5,
        "z": 8
    }
    >>> handle_dict(d, {"w":lambda x,z: x**z})
    >>> d
    {
        "w": "→(x z)",
        "x": 5,
        "z": 8
    }
    """
    data = data.copy()
    for k, v in dictlike.items():
        if v is None:
            del data[k]
        else:
            data[k] = lazify(data, k, v, rnd) if callable(v) else v
    return data


def lazify(data, output_field: Union[list, str], f, rnd) -> Union[dict, LazyVal]:
    from ldict.parameter.let import Let
    config, f = (f.config, f.f) if isinstance(f, Let) else ({}, f)
    input_fields, parameters = extract_input(f)
    dictstr = extract_dictstr(f)
    for par in extract_implicit_input(dictstr):
        if par not in config:
            raise Exception(f"Parameter '{par}' value is not available:", config)
        input_fields.append(config[par])
    deps = prepare_deps(data, input_fields, parameters, config, rnd)
    if output_field == "extract":
        return {k: LazyVal(k, f, deps, multi_output=True) for k in extract_output(f, dictstr, parameters)}
    else:
        return LazyVal(output_field, f, deps, multi_output=False)


def prepare_deps(data, input, parameters, config, rnd):
    """Build a dict containing all needed dependencies (values) to apply a function: input fields and parameters.

    Parameter values are given in config or sampled according to a range using rnd.
    A range is specified as the default value of the parameter in the function signature.
    """
    deps = {}
    for k, v in parameters.items():
        if isinstance(v, list):
            deps[k] = rnd.choice(expand(v))
        elif k in config:
            deps[k] = config[k]
    deps.update({k: data[k] for k in input})
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
    return list(list2progression(lst))


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
    diff1 = lst[1] - lst[0]
    diff2 = lst[2] - lst[1]
    ratio1 = lst[1] / lst[0]
    ratio2 = lst[2] / lst[1]
    newlst = [lst[0], lst[1], ..., lst[-1]]
    if diff1 == diff2:
        return AP(*newlst)
    elif ratio1 == ratio2:
        return GP(*newlst)
    else:
        raise InconsistentLange(f"Cannot identify whether this is a G. or A. progression: {lst}")


def rho(c, digits):
    return digits // 2 * "-" + str(c).rjust(digits // 2, ".")


def create_lazies(f: Callable, input, implicit_input, output, data, config, parameters, rnd, multi_output):
    deps = {}
    for k, v in parameters.items():
        if isinstance(v, list):
            deps[k] = rnd.choice(expand(v))
        elif k in config:
            deps[k] = config[k]
    deps.update({k: data[k] for k in input})
    print(11111111, implicit_input)
    deps.update({(k := config[par]): data[k] for par in implicit_input})
    config.clear()
    reordered_data = {"id": None, "ids": {}}
    if len(output) == 1:
        reordered_data[output[0]] = LazyVal(output[0], f, deps, multi_output=multi_output)
    else:
        for field in output:
            reordered_data[field] = LazyVal(field, f, deps, multi_output=True)
    for k, v in data.items():
        if k not in reordered_data:
            reordered_data[k] = v
    data.clear()
    data.update(reordered_data)
