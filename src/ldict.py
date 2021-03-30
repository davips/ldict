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
#  Relevant employers or funding agencies will be notified accordingly.

# Dict typing ineritance initially based on https://stackoverflow.com/a/64323140/9681577
import json
import re
from inspect import signature, getsourcelines
from typing import Iterator, TypeVar, Iterable, Dict

from data import process
from garoupa.hash import identity

VT = TypeVar('VT')


class Ldict(Dict[str, VT]):
    def __init__(self, /, keepblob=False, _dictionary=None, **kwargs) -> None:
        """Uniquely identified lazy dict for serializable pairs str->value
        (serializable in the project 'orjson' sense).
        Usage:
        >>> from ldict import ldict
        >>> print(ldict(X=123123))
        {
            "id": "0000000000000000000007LGxmlWgkN894sZEneXuIp",
            "X": 123123,
            "id_...": "..."
        }
        """
        super().__init__()
        self.data: Dict[str, VT] = {}
        self.hashes = {}
        self.blobs = {}
        self.keepblob = keepblob
        self.hash = identity
        if _dictionary is not None:
            self.update(_dictionary)  # REMINDER: this calls setitem() on self.data.
        if kwargs:
            self.update(kwargs)

    @property
    def n(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124).n
        108990846591764296187947743094879269859
        """
        return self.hash.n

    @property
    def id(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124).id
        '0000000000000000000002Uir4UFhytZSbfZqV8rALj'
        """
        return self.hash.id

    @property
    def ids(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124).ids
        {'x': '0000000000000000000002Uir4UFhytZSbfZqV8rALj'}
        """
        return {f: h.id for f, h in self.hashes.items()}

    @property
    def all(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> print(ldict(x=134124, y= 56).all)
        {
            "id": "\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;203m\x1b[1mt\x1b[0m\x1b[38;5;173m\x1b[1mT\x1b[0m\x1b[38;5;167m\x1b[1mH\x1b[0m\x1b[38;5;167m\x1b[1ma\x1b[0m\x1b[38;5;173m\x1b[1mz\x1b[0m\x1b[38;5;167m\x1b[1mK\x1b[0m\x1b[38;5;203m\x1b[1m6\x1b[0m\x1b[38;5;167m\x1b[1mb\x1b[0m\x1b[38;5;209m\x1b[1mE\x1b[0m\x1b[38;5;167m\x1b[1m5\x1b[0m\x1b[38;5;209m\x1b[1mU\x1b[0m\x1b[38;5;203m\x1b[1mI\x1b[0m\x1b[38;5;167m\x1b[1m1\x1b[0m\x1b[38;5;203m\x1b[1mQ\x1b[0m\x1b[38;5;203m\x1b[1mN\x1b[0m\x1b[38;5;167m\x1b[1mP\x1b[0m\x1b[38;5;203m\x1b[1mo\x1b[0m\x1b[38;5;203m\x1b[1mJ\x1b[0m\x1b[38;5;203m\x1b[1mc\x1b[0m\x1b[38;5;173m\x1b[1mD\x1b[0m\x1b[38;5;203m\x1b[1mI\x1b[0m",
            "x": 134124,
            "id_x": "\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;97m\x1b[1m2\x1b[0m\x1b[38;5;98m\x1b[1mU\x1b[0m\x1b[38;5;62m\x1b[1mi\x1b[0m\x1b[38;5;63m\x1b[1mr\x1b[0m\x1b[38;5;61m\x1b[1m4\x1b[0m\x1b[38;5;98m\x1b[1mU\x1b[0m\x1b[38;5;97m\x1b[1mF\x1b[0m\x1b[38;5;98m\x1b[1mh\x1b[0m\x1b[38;5;63m\x1b[1my\x1b[0m\x1b[38;5;99m\x1b[1mt\x1b[0m\x1b[38;5;98m\x1b[1mZ\x1b[0m\x1b[38;5;62m\x1b[1mS\x1b[0m\x1b[38;5;62m\x1b[1mb\x1b[0m\x1b[38;5;62m\x1b[1mf\x1b[0m\x1b[38;5;98m\x1b[1mZ\x1b[0m\x1b[38;5;63m\x1b[1mq\x1b[0m\x1b[38;5;98m\x1b[1mV\x1b[0m\x1b[38;5;61m\x1b[1m8\x1b[0m\x1b[38;5;63m\x1b[1mr\x1b[0m\x1b[38;5;97m\x1b[1mA\x1b[0m\x1b[38;5;62m\x1b[1mL\x1b[0m\x1b[38;5;62m\x1b[1mj\x1b[0m",
            "y": 56,
            "id_y": "\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;59m\x1b[1m6\x1b[0m\x1b[38;5;65m\x1b[1mB\x1b[0m\x1b[38;5;61m\x1b[1mo\x1b[0m\x1b[38;5;66m\x1b[1mS\x1b[0m\x1b[38;5;66m\x1b[1mj\x1b[0m\x1b[38;5;66m\x1b[1ml\x1b[0m\x1b[38;5;66m\x1b[1mQ\x1b[0m\x1b[38;5;66m\x1b[1mU\x1b[0m\x1b[38;5;59m\x1b[1m6\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;240m\x1b[1mH\x1b[0m\x1b[38;5;66m\x1b[1ml\x1b[0m\x1b[38;5;61m\x1b[1mq\x1b[0m\x1b[38;5;65m\x1b[1m8\x1b[0m\x1b[38;5;67m\x1b[1mz\x1b[0m\x1b[38;5;241m\x1b[1mJ\x1b[0m\x1b[38;5;61m\x1b[1mn\x1b[0m\x1b[38;5;61m\x1b[1mm\x1b[0m\x1b[38;5;66m\x1b[1mi\x1b[0m\x1b[38;5;65m\x1b[1m9\x1b[0m\x1b[38;5;243m\x1b[1mR\x1b[0m\x1b[38;5;65m\x1b[1m8\x1b[0m"
        }
        """
        return self.__repr__(all=True)

    def show(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124, y= 56).show()
        {
            "id": "\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;203m\x1b[1mt\x1b[0m\x1b[38;5;173m\x1b[1mT\x1b[0m\x1b[38;5;167m\x1b[1mH\x1b[0m\x1b[38;5;167m\x1b[1ma\x1b[0m\x1b[38;5;173m\x1b[1mz\x1b[0m\x1b[38;5;167m\x1b[1mK\x1b[0m\x1b[38;5;203m\x1b[1m6\x1b[0m\x1b[38;5;167m\x1b[1mb\x1b[0m\x1b[38;5;209m\x1b[1mE\x1b[0m\x1b[38;5;167m\x1b[1m5\x1b[0m\x1b[38;5;209m\x1b[1mU\x1b[0m\x1b[38;5;203m\x1b[1mI\x1b[0m\x1b[38;5;167m\x1b[1m1\x1b[0m\x1b[38;5;203m\x1b[1mQ\x1b[0m\x1b[38;5;203m\x1b[1mN\x1b[0m\x1b[38;5;167m\x1b[1mP\x1b[0m\x1b[38;5;203m\x1b[1mo\x1b[0m\x1b[38;5;203m\x1b[1mJ\x1b[0m\x1b[38;5;203m\x1b[1mc\x1b[0m\x1b[38;5;173m\x1b[1mD\x1b[0m\x1b[38;5;203m\x1b[1mI\x1b[0m",
            "x": 134124,
            "id_x": "\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;97m\x1b[1m2\x1b[0m\x1b[38;5;98m\x1b[1mU\x1b[0m\x1b[38;5;62m\x1b[1mi\x1b[0m\x1b[38;5;63m\x1b[1mr\x1b[0m\x1b[38;5;61m\x1b[1m4\x1b[0m\x1b[38;5;98m\x1b[1mU\x1b[0m\x1b[38;5;97m\x1b[1mF\x1b[0m\x1b[38;5;98m\x1b[1mh\x1b[0m\x1b[38;5;63m\x1b[1my\x1b[0m\x1b[38;5;99m\x1b[1mt\x1b[0m\x1b[38;5;98m\x1b[1mZ\x1b[0m\x1b[38;5;62m\x1b[1mS\x1b[0m\x1b[38;5;62m\x1b[1mb\x1b[0m\x1b[38;5;62m\x1b[1mf\x1b[0m\x1b[38;5;98m\x1b[1mZ\x1b[0m\x1b[38;5;63m\x1b[1mq\x1b[0m\x1b[38;5;98m\x1b[1mV\x1b[0m\x1b[38;5;61m\x1b[1m8\x1b[0m\x1b[38;5;63m\x1b[1mr\x1b[0m\x1b[38;5;97m\x1b[1mA\x1b[0m\x1b[38;5;62m\x1b[1mL\x1b[0m\x1b[38;5;62m\x1b[1mj\x1b[0m",
            "y": 56,
            "id_y": "\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;59m\x1b[1m6\x1b[0m\x1b[38;5;65m\x1b[1mB\x1b[0m\x1b[38;5;61m\x1b[1mo\x1b[0m\x1b[38;5;66m\x1b[1mS\x1b[0m\x1b[38;5;66m\x1b[1mj\x1b[0m\x1b[38;5;66m\x1b[1ml\x1b[0m\x1b[38;5;66m\x1b[1mQ\x1b[0m\x1b[38;5;66m\x1b[1mU\x1b[0m\x1b[38;5;59m\x1b[1m6\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;240m\x1b[1mH\x1b[0m\x1b[38;5;66m\x1b[1ml\x1b[0m\x1b[38;5;61m\x1b[1mq\x1b[0m\x1b[38;5;65m\x1b[1m8\x1b[0m\x1b[38;5;67m\x1b[1mz\x1b[0m\x1b[38;5;241m\x1b[1mJ\x1b[0m\x1b[38;5;61m\x1b[1mn\x1b[0m\x1b[38;5;61m\x1b[1mm\x1b[0m\x1b[38;5;66m\x1b[1mi\x1b[0m\x1b[38;5;65m\x1b[1m9\x1b[0m\x1b[38;5;243m\x1b[1mR\x1b[0m\x1b[38;5;65m\x1b[1m8\x1b[0m"
        }
        """
        return print(self.all)

    @property
    def perm(self):
        """
        For new data, it is always the identity permutation.
        Usage:
        >>> from ldict import ldict
        >>> a = ldict(x=134124)
        >>> a.perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> (a + a).perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> b = a + ldict(y=134124)
        >>> b.perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> f = lambda x: {'z': x ** 2}
        >>> print(b >> f)
        {
            "id": "DJCI4NHm3GUzL4KQt7W3dWh3JkAGSMz5Ttx9lzoNnMQ",
            "x": 134124,
            "y": 134124,
            "z": "<unevaluated lazy field>",
            "id_...": "..."
        }
        """
        return self.hash.perm

    def __add__(self, other):
        return self.update(other)

    @property
    def hex(self):
        return hex(self.n)[2:]

    def __getitem__(self, field: str) -> VT:
        if field in self.data:
            content = self.data[field]
            if callable(content):
                self.data[field] = self.data[field](**self._getargs(field, content))
                return self.data[field]
            else:
                return self.data[field]
        raise KeyError(field)

    def __rshift__(self, f):
        """Used for multiple return values, or to avoid inplace update."""
        if not callable(f):
            raise Exception("f should be callable.")
        lines = getsourcelines(f)[0]
        returns = [line for line in lines if "return" in line]
        if len(returns) != 1:
            if "lambda" not in lines[0]:
                raise Exception(f"A single 'return <dict>' statement is expected. Not {len(returns)} occurrences."
                                f"Lambdas should be inline.")
            returns = [lines[0]]
        rx = r"(?:[\"'])([a-zA-Z]+[a-zA-Z0-9_]*)(?:[\"'])"
        output_fields = re.findall(rx, returns[0])
        if not output_fields:
            raise Exception("Missing some structure in the function body.")
        fargs = signature(f).parameters.keys()
        self.update({k: self._trigger(k, f, fargs) for k in output_fields})
        return self

    def _getargs(self, field, f, fargs=None):
        fargs = fargs or signature(f).parameters.keys()
        dic = {}
        for k in fargs:
            if k not in self:
                print(self)
                raise Exception(f"Missing field {k} needed by {f} to calculate field {field}.")
            dic[k] = self[k]
        return dic

    def _trigger(self, field, f, fargs):
        def closure():
            dic = self._getargs(field, f, fargs)
            self.update(**f(**dic))
            return self[field]

        return closure

    def __hash__(self):
        return self.n

    def __str__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if not all and k.startswith("id_"):
                del dic[k]
            elif callable(v):
                dic[k] = "<unevaluated lazy field>"
        dic["id_..."] = "..."
        return json.dumps(dic, indent=4)

    def __repr__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if callable(v):
                dic[k] = "<unevaluated lazy field>"
            if not all and k.startswith("id_"):
                del dic[k]
        if not all:
            dic["ids_..."] = "..."
        txt = json.dumps(dic, indent=4)
        for k, v in dic.items():
            if k == "id":
                txt = txt.replace(dic[k], self.hash.idc)
            elif all and k.startswith("id_"):
                txt = txt.replace(dic[k], self.hashes[k[3:]].idc)
        return txt

    def __eq__(self, other):
        if isinstance(other, Ldict):
            return self.n == other.n
        return NotImplemented

    def __contains__(self, field: str) -> bool:
        return field in self.data

    def __delitem__(self, field: str) -> None:
        del self.data[field]
        raise Exception("Not implemented")

    def __getattr__(self, item):
        if item in self:
            return self[item]
        return self.__getattribute__(item)

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.data)

    def __setitem__(self, field: str, value: VT) -> None:
        self.data["id"] = None
        self.data[field] = value
        fid = f"id_{field}"
        h = None
        if fid not in self.data:
            h, blob = process(field, value)
            if blob and self.keepblob:
                self.blobs[field] = blob
            self.hashes[field] = h
        self.hash *= self.hashes[field]
        self.data["id"] = self.hash.id
        if h:
            self.data["id_" + field] = h.id

    @classmethod
    def fromkeys(cls, iterable: Iterable[str], value: VT) -> "Ldict":
        """Create a new dictionary with keys from `iterable` and values set to `value`.

        Args:
            iterable: A collection of keys.
            value: The default value. It defaults to None.
            All of the values refer to just a single instance,
            so it generally doesn’t make sense for value to be a mutable object such as an empty list.
            To get distinct values, use a dict comprehension instead.

        Returns:
            A new instance of Dict.
        """
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def keys(self):
        yield from self.data.keys()

    def update(self, other=(), /, **kwds) -> "Ldict":
        """Update the dictionary with the key/value pairs from other, overwriting existing keys. Return self.
        Usage:
        >>> from ldict import ldict
        >>> a = ldict(x=123)
        >>> print(a)
        {
            "id": "0000000000000000000006pnWvaKVQbhfaIl82A1WD6",
            "x": 123,
            "id_...": "..."
        }
        >>> b = ldict(y="some text")
        >>> print(b)
        {
            "id": "00000000000000000000001Q5vqu6zuQ864lVfx25Vw",
            "y": "some text",
            "id_...": "..."
        }
        >>> print(b.update(a))
        {
            "id": "0000000000000000000006rDcrREcQW7ngNWdi73bj2",
            "y": "some text",
            "x": 123,
            "id_...": "..."
        }
        """
        kwds.update(other)
        ids = {}
        for field, value in kwds.items():
            if not field.startswith("id_") and field != "id":
                idk = f"id_{field}"
                self[field] = value
                if idk in kwds:
                    ids[idk] = kwds[idk]
                    if isinstance(other, Ldict):
                        self.hashes[field] = other.hashes[field]
                        self.keepblob = other.keepblob
                        if field in other.blobs:
                            self.blobs[field] = other.blobs[field]
        self.data.update(ids)
        return self


ldict = Ldict
