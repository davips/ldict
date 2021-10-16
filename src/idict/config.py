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
from typing import TypeVar

VT = TypeVar("VT")

GLOBAL = {
    "compression_cache": {},
    "compression_cachesize": 0,
    "compression_cachelimit": 1_000_000_000
}


def setup(compression_cachelimit_MB: float = None):
    """
    Global behavior when memoizing blobs inside idict objects

    Parameters
    ----------
    compression_cachelimit_MB
        Amount of MBs reserved for keeping compressed values in memory.
        Higher values accelerate persisting original values as compression is already done at hashing.
    """
    if compression_cachelimit_MB is not None:
        GLOBAL["compression_cachelimit"] = int(compression_cachelimit_MB * 1_000_000)