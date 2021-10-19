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

from typing import Union

from lange import AP, GP

from ldict.core.inspection import extract_implicit_input, extract_output, extract_returnstr, extract_dictstr
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
    config, f = (f.config, f.f) if isinstance(f, AbstractLet) else ({}, f)
    input_fields, parameters = extract_input(f)
    returnstr = extract_returnstr(f)
    if multi_output:
        returnstr = extract_dictstr(returnstr)
    for par in extract_implicit_input(returnstr):
        if par not in config:  # pragma: no cover
            raise Exception(f"Parameter '{par}' value is not available:", config)
        input_fields.append(config[par])
    deps = prepare_deps(data, input_fields, parameters, config, rnd)
    if output_field == "extract":
        lazies = []
        dic = {k: LazyVal(k, f, deps, lazies) for k in extract_output(f, returnstr, deps)}
        lazies.extend(dic.values())
        return dic
    else:
        return LazyVal(output_field, f, deps, None)


def prepare_deps(data, input, parameters, config, rnd):
    """Build a dict containing all needed dependencies (values) to apply a function: input fields and parameters.

    Parameter values are given in config or sampled according to a range using rnd.
    A range is specified as the default value of the parameter in the function signature.
    """
    deps = {}
    for k, v in parameters.items():
        if k in config:
            v = config[k]
        if isinstance(v, list):
            if rnd is None:  # pragma: no cover
                raise UndefinedSeed("Missing Random object before parameterized function application.")
            deps[k] = rnd.choice(expand(v))
        elif v is None:  # pragma: no cover
            raise DependenceException(f"'None' value for parameter {k}.", deps.keys())
        else:
            deps[k] = v
    for k in input:
        if k not in data:  # pragma: no cover
            raise DependenceException(f"Missing field {k}.", data.keys())
        if data[k] is None:  # pragma: no cover
            raise DependenceException(f"'None' value for field {k}.", data.keys())
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
