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
import operator
from functools import reduce
from random import Random

from ldict.exception import WrongId, MissingIds, InconsistentIds


def initialize(d, identity, readonly, let):  # pragma:  cover
    d.readonly, d.digits, d.version, d.let = readonly, identity.digits, identity.version, let or {}
    d.hosh = d.identity = identity
    d.blobs, d.hashes, d.hoshes = {}, {}, {}
    d.history, d.last = {}, None
    d.rnd = Random()


def build_from_dict(dic, self):
    """
    >>> dic = {
    ...     "id": "UU_2e6d9ba08a7bc90dcea614b3a68ace6c9acea",
    ...     "ids": {"x": "XX_abcdefabcdefabcdefabcdefabcdefabcdefa", "y": "YY_23445235bcdefabcdefabcdefabcdefabcdef"},
    ...     "x": None,
    ...     "y": None
    ... }
    >>> from ldict import ldict
    >>> ldict(dic).show(colored=False)
    {
        "id": "UU_2e6d9ba08a7bc90dcea614b3a68ace6c9acea",
        "x": null,
        "y": null,
        "ids": {
            "x": "XX_abcdefabcdefabcdefabcdefabcdefabcdefa",
            "y": "YY_23445235bcdefabcdefabcdefabcdefabcdef"
        }
    }
    """
    id = dic["id"]
    if not (ids := dic.pop("ids", False)):  # pragma: no cover
        raise MissingIds(f"id {id} provided but ids missing while importing dict-like")
    if not isinstance(id, str):  # pragma: no cover
        raise WrongId(f"id {id} provided should be str, not {type(id)}")
    if (fields := list(dic.keys())[1:]) != list(ids.keys()):  # pragma: no cover
        raise InconsistentIds(f"'ids' ({ids.keys()}) should match provided fields ({fields}")
    hosh = self.hosh.ø * dic["id"]
    hoshes = {k: self.hosh.ø * v for k, v in ids.items()}
    if hosh != (res := reduce(operator.mul, hoshes.values())):  # pragma: no cover
        raise InconsistentIds(f"'id' ({dic['id']}) differs from {res}, which is the product of 'ids' ({ids.values()}).")
    self.hoshes = hoshes
    self.hosh = hosh
    self.data.update(dic)
    self.data["ids"] = ids.copy()
