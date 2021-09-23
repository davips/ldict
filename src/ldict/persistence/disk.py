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
import shelve
from typing import TypeVar

from ldict.persistence.cache import Cache

VT = TypeVar("VT")


class Disk(Cache):  # pragma:  cover
    """Save to/retrieve from disk.

    Based on built-in module shelve. Open and close at every transaction.
    To keep open, please use shelve context manager itself.

    >>> d = Disk("/tmp/test.db")
    >>> d["x"] = 5
    >>> d["x"]
    5
    >>> for k,v in d.items():
    ...     print(k, v)
    x 5
    >>> "x" in d
    True
    >>> len(d)
    1
    >>> d2 = d.copy()
    >>> del d["x"]
    >>> "x" in d
    False
    >>> d
    Disk→<class 'shelve.DbfilenameShelf'>
    >>> list(d2.keys())
    ['x']
    """

    def __init__(self, file):
        super().__init__()
        self.file = file

    def __contains__(self, item):
        with shelve.open(self.file, "c") as db:
            return item in db

    def __setitem__(self, key, value):
        with shelve.open(self.file, "c") as db:
            db[key] = value

    def __getitem__(self, key):
        with shelve.open(self.file, "c") as db:
            return db[key]

    def __delitem__(self, key):
        with shelve.open(self.file, "c") as db:
            del db[key]

    def __len__(self):
        with shelve.open(self.file, "c") as db:
            return len(db)

    def __iter__(self):
        with shelve.open(self.file, "c") as db:
            keys = list(db.keys())
        return iter(keys)

    def __repr__(self):
        with shelve.open(self.file, "c") as db:
            return "Disk→" + str(type(db))

    def copy(self):
        with shelve.open(self.file, "c") as db:
            dic = dict(db)
            return dic

    def keys(self):
        return iter(self)

    def items(self):
        for k in self.keys():
            yield k, self[k]
