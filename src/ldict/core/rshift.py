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

from typing import Callable

from lange import AP, GP
from orjson import OPT_SORT_KEYS, dumps

from ldict.core.history import extend_history
from ldict.data import removal_id
from ldict.exception import InconsistentLange, OverwriteException
from ldict.lazy import Lazy


def handle_dict(d, dictlike):
    """
    >>> from ldict import ldict
    >>> d = ldict(x=5, y=7, z=8)
    >>> handle_dict(d, {"y":None})
    >>> d.show(colored=False)
    {
        "id": "dejCAhZMpV8N1ZR8s3HUnCi0-LP............y",
        "ids": {
            "x": ".T_f0bb8da3062cc75365ae0446044f7b3270977",
            "y": "gDcc4Rgrs4C3tMZUcb1Fp9KO53R............y",
            "z": "7q_3c95f44b01eb0f9e2da3bda1665567bc21bde"
        },
        "x": 5,
        "y": null,
        "z": 8
    }
    >>> handle_dict(d, {"w":lambda x,z: x**z})
    >>> d.show(colored=False)
    {
        "id": "p.82XiVd66i7iZcpKpspLqJjTIqs3d9r2rr8kHNE",
        "ids": {
            "w": "APe82rIDSl0OEtKebkaueUlhuQts3d9r2rr8kHN5",
            "x": ".T_f0bb8da3062cc75365ae0446044f7b3270977",
            "y": "gDcc4Rgrs4C3tMZUcb1Fp9KO53R............y",
            "z": "7q_3c95f44b01eb0f9e2da3bda1665567bc21bde"
        },
        "w": "→(x z)",
        "x": 5,
        "y": null,
        "z": 8
    }
    """
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
    """
    >>> from ldict import Ø, setup
    >>> setup(history=True)  # Keep history of ids of all applied functions.
    >>> d = Ø >> {"x": 5, "y": 7}
    >>> d.show(colored=False)
    {
        "id": "mP_2d615fd34f97ac906e162c6fc6aedadc4d140",
        "ids": {
            "x": ".T_f0bb8da3062cc75365ae0446044f7b3270977",
            "y": "mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8"
        },
        "x": 5,
        "y": 7
    }
    >>> d >>= {"x": None}  # Remove content by key.
    >>> d.show(colored=False)
    {
        "id": "CXYCCgcFV6pRo6hXABwYD1393j4000000000000y",
        "ids": {
            "x": "ot0SdHVcTM12wYEmUc1.ZaSmqt5000000000000y",
            "y": "mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8"
        },
        "x": null,
        "y": 7
    }
    >>> from ldict import decolorize
    >>> decolorize(str(d.history)) == '{mP_2d615fd34f97ac906e162c6fc6aedadc4d140: {mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8, .T_f0bb8da3062cc75365ae0446044f7b3270977}, --------------------...................x: None}'
    True
    """
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


def solve(hoshes, output, uf):
    """
    >>> from ldict import ldict
    >>> a = ldict(x=3)
    >>> a.show(colored=False)
    {
        "id": "WB_e55a47230d67db81bcc1aecde8f1b950282cd",
        "ids": {
            "x": "WB_e55a47230d67db81bcc1aecde8f1b950282cd"
        },
        "x": 3
    }
    >>> a >>= (lambda x: {"x": x+2})
    >>> a.show(colored=False)
    {
        "id": "j9i-.G4WwbjZsi8V.dLkkb5hhPDYDDRQkGiQ6qJ8",
        "ids": {
            "x": "j9i-.G4WwbjZsi8V.dLkkb5hhPDYDDRQkGiQ6qJ8"
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
        "id": "4k236R0oT.PI6-c2KLgmahWdNOzzkEFdqK4B1zjh",
        "ids": {
            "x": "RonX9OcL1opfeXE9CJXL1LtpNBqgmEFdqG4B1zji",
            "y": "ofEb.nRSYsUsgAnnyp4KYFovZaUOV6000sv....-",
            "w": "ng_5dad44381c5ac2a4c1bfe594d68a486791c45",
            "z": "vY_6b073e90b397af73e43c1e6c4777abeeadb9f"
        },
        "x": "→(w x y)",
        "y": "→(w x y)",
        "w": 2,
        "z": 1
    }
    """
    previous = uf.ø
    for k, v in hoshes.items():
        if k not in output:
            previous *= v
    return uf * ~previous


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
        reordered_data[output[0]] = Lazy(output[0], f, deps, multi_output=multi_output)
    else:
        for field in output:
            reordered_data[field] = Lazy(field, f, deps, multi_output=True)
    for k, v in data.items():
        if k not in reordered_data:
            reordered_data[k] = v
    data.clear()
    data.update(reordered_data)


def update_identity(output, data, fhosh, hosh, hoshes, config):
    if config:
        fhosh *= dumps(config, option=OPT_SORT_KEYS)  # d' = d * ħ(config) * f
    uf = hosh * fhosh
    data["id"] = uf.id
    ids = list(data.keys())[2:]
    data["ids"].clear()
    ufu_1 = solve(hoshes, output, uf)
    oldhoshes = hoshes.copy()
    hoshes.clear()
    if len(output) == 1:
        field = output[0]
        hoshes[field] = ufu_1 if field in ids else uf * ~hosh
        data["ids"][field] = hoshes[field].id
    else:
        acc = hosh.ø
        c = 0
        for i, field in enumerate(output):
            if i < len(output) - 1:
                field_hosh = ufu_1 * rho(c, hosh.digits)
                c += 1
                acc *= field_hosh
            else:
                field_hosh = ~acc * ufu_1
            hoshes[field] = field_hosh
            data["ids"][field] = hoshes[field].id

    for field in ids:
        if field not in hoshes:
            hoshes[field] = oldhoshes[field]
            data["ids"][field] = hoshes[field].id

    return uf
