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
from idict.data import fhosh
from ldict.core.rshift import lazify


def application(self, other, f, f_hosh):
    # noinspection PyUnboundLocalVariable
    f_hosh *= fhosh(f, self.identity.version)  # d' = d * ħ(config) * f
    frozen = self.frozen >> other
    uf = self.hosh * f_hosh
    ufu_1 = lambda: solve(self.hoshes, frozen.returned, uf)

    # Reorder items.
    newdata, newhoshes, newblobs, newhashes, = {}, {}, self.blobs.copy(), self.hashes.copy()
    noutputs = len(frozen.returned)
    if noutputs == 1:
        k = frozen.returned[0]
        newdata[k] = frozen.data[k]
        newhoshes[k] = ufu_1() if k in self.ids else uf * ~self.hosh
    else:
        ufu_1 = ufu_1()
        acc = self.identity
        c = 0
        for i, k in enumerate(frozen.returned):
            newdata[k] = frozen.data[k]
            if i < noutputs - 1:
                field_hosh = ufu_1 * rho(c, self.identity.digits)
                c += 1
                acc *= field_hosh
            else:
                field_hosh = ~acc * ufu_1
            newhoshes[k] = field_hosh
            if k in newblobs[k]:
                del newblobs[k]
            if k in newhashes[k]:
                del newhashes[k]
    for k in self.ids:
        if k not in newdata:
            newhoshes[k] = self.hoshes[k]
            newdata[k] = frozen.data[k]

    cloned_internals = dict(blobs=newblobs, hashes=newhashes, hoshes=newhoshes, hosh=uf)
    return self.clone(newdata, _cloned=cloned_internals)


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


# def handle_dict(data, dictlike, rnd):
#     for k, v in dictlike.items():
#         if v is None:
#             removal_hosh = remove(k, d.data, d.hosh, d.hoshes, d.hashes)
#             d.hosh *= removal_hosh
#             d.last = extend_history(d.history, d.last, removal_hosh)
#         elif k not in ["id", "ids"]:
#             if k in d.data:
#                 raise OverwriteException(f"Cannot overwrite field ({k}) via value insertion through >>")
#             d[k] = v
#
#
# def remove(key, data, hosh, hoshes, hashes):
#     fhosh = hosh.ø * removal_id(hosh.delete, key)
#     it = iter(hoshes.items())
#     while (pair := next(it))[0] != key:
#         pass
#     oldfield_hosh = pair[1]
#     right = hosh.ø
#     for k, v in it:
#         right *= v
#     field_hosh = oldfield_hosh * right * fhosh * ~right
#
#     data["id"] = hosh.id
#     data[key] = None
#     data["ids"][key] = field_hosh.id
#     hoshes[key] = field_hosh
#     if key in hashes:
#         del hashes[key]
#
#     return fhosh


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


def rho(c, digits):
    return digits // 2 * "-" + str(c).rjust(digits // 2, ".")
