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
import pickle

import lz4.frame as lz4

from idict.config import GLOBAL


def pack(obj):
    r"""
    >>> from idict import setup
    >>> setup(compression_cachelimit_MB=0.000_100)
    >>> memo = GLOBAL["compression_cache"] = {}
    >>> GLOBAL["compression_cachesize"] = 0
    >>> b = b"000011"
    >>> pack(b)
    b'\x04"M\x18h@\x15\x00\x00\x00\x00\x00\x00\x006\x13\x00\x00\x00R\x80\x05\x95\n\x00\x01\x00\xa0C\x06000011\x94.\x00\x00\x00\x00'
    >>> memo[id(b)]["unpacked"]
    b'000011'
    >>> len(memo), GLOBAL["compression_cachesize"], GLOBAL["compression_cachelimit"]
    (1, 42, 100)
    >>> pack(b"asd")
    b'\x04"M\x18h@\x12\x00\x00\x00\x00\x00\x00\x00\xd9\x10\x00\x00\x00R\x80\x05\x95\x07\x00\x01\x00pC\x03asd\x94.\x00\x00\x00\x00'
    >>> len(memo), GLOBAL["compression_cachesize"], GLOBAL["compression_cachelimit"]
    (2, 81, 100)
    >>> len(pack(b"123"))
    39
    >>> len(memo), GLOBAL["compression_cachesize"], GLOBAL["compression_cachelimit"]
    (2, 78, 100)
    """
    memid = id(obj)
    memo = GLOBAL["compression_cache"]
    if memid in memo:
        if obj is memo[memid]["unpacked"]:
            return memo[memid]["packed"]
        else:
            # rare collision
            GLOBAL["compression_cachesize"] -= memo[memid]["packed"]
            del memo[memid]

    blob = lz4.compress(pickle.dumps(obj, protocol=5))
    GLOBAL["compression_cachesize"] += len(blob)
    memo[memid] = {"unpacked": obj, "packed": blob}

    # LRU
    keys = iter(list(memo.keys()))
    while len(memo) > 0 and GLOBAL["compression_cachesize"] > GLOBAL["compression_cachelimit"]:
        k = next(keys)
        v = memo.pop(k)["packed"]
        GLOBAL["compression_cachesize"] -= len(v)

    return blob


def unpack(blob):
    r"""
    >>> unpack(b'\x04"M\x18h@\x15\x00\x00\x00\x00\x00\x00\x006\x13\x00\x00\x00R\x80\x05\x95\n\x00\x01\x00\xa0C\x06000011\x94.\x00\x00\x00\x00')
    b'000011'
    """
    return pickle.loads(lz4.decompress(blob))
