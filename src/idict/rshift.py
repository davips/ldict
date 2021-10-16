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
from ldict.core.rshift import lazify


def ihandle_dict(data, dictlike, rnd):
    """
    >>> from idict.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> d = idict(x=5, y=7, z=8)
    >>> di = ihandle_dict(d.frozen.data, {"y":None}, None)
    >>> di
    {'x': 5, 'y':None, 'z': 8}
    >>> ihandle_dict(di, {"w":lambda x,z: x**z}, None)
    {'x': 5, 'z': 8, 'w': →(x z)}
    """
    data = data.copy()
    for k, v in dictlike.items():
        if v is None:
            data[k] = None
        else:
            from ldict.core.ldict_ import Ldict
            if callable(v):
                data[k] = lazify(data, k, v, rnd, multi_output=False)
            elif isinstance(v, Ldict):
                data[k] = v.frozen
            else:
                data[k] = v
    return data


def handle_dict(data, dictlike, rnd):
    for k, v in dictlike.items():
        if v is None:
            removal_hosh = remove(k, d.data, d.hosh, d.hoshes, d.hashes)
            d.hosh *= removal_hosh
            d.last = extend_history(d.history, d.last, removal_hosh)
        elif k not in ["id", "ids"]:
            if k in d.data:
                raise OverwriteException(f"Cannot overwrite field ({k}) via value insertion through >>")
            d[k] = v


def remove(key, data, hosh, hoshes, hashes):
    fhosh = hosh.ø * removal_id(hosh.delete, key)
    it = iter(hoshes.items())
    while (pair := next(it))[0] != key:
        pass
    oldfield_hosh = pair[1]
    right = hosh.ø
    for k, v in it:
        right *= v
    field_hosh = oldfield_hosh * right * fhosh * ~right

    data["id"] = hosh.id
    data[key] = None
    data["ids"][key] = field_hosh.id
    hoshes[key] = field_hosh
    if key in hashes:
        del hashes[key]

    return fhosh
