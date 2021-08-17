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
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
from typing import Dict

from ldict_modules.exception import FromØException
from ldict_modules.ldict_ import Ldict


class Empty(Ldict):
    def __init__(self, version):
        super().__init__(version=version)

    def __rshift__(self, other):
        """
        Usage:

        >>> from ldict import ø
        >>> d = ø >> {"x": 2}
        >>> d.show(colored=False)
        {
            "id": "00000000000dc-DMDXCtigJFu0bLt-KK",
            "ids": {
                "x": "00000000000dc-DMDXCtigJFu0bLt-KK"
            },
            "x": 2
        }
        >>> from ldict import Ø
        >>> d = Ø >> {"x": 2}
        >>> d.show(colored=False)
        {
            "id": "000000000000000000000c3aop1df5AZXCRMY3yInQeUYccGQRclWo8TvfKPB4YT",
            "ids": {
                "x": "000000000000000000000c3aop1df5AZXCRMY3yInQeUYccGQRclWo8TvfKPB4YT"
            },
            "x": 2
        }
        """
        if not isinstance(other, Dict):
            raise FromØException(f"Empty ldict (ø) can only be passed to a dict-like object, not {type(other)}.")
        return Ldict(other, version=self.version)
