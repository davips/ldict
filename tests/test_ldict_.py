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
from collections import namedtuple
from unittest import TestCase

import pytest
from sys import maxsize

from ldict import ldict, Ø
from ldict.exception import DependenceException, NoInputException, WrongKeyType, ReadOnlyLdict, \
    OverwriteException


class TestLdict(TestCase):
    def test_identity(self):
        a = Ø >> {"x": 1, "y": 2}
        b = a >> Ø
        self.assertEqual(a, b)
        self.assertFalse(a == 123)
        self.assertNotEqual(a, 123)
        self.assertEqual(a.hosh.n % maxsize, hash(a))
        d = {'id': 'Tc_fb3057e399a385aaa6ebade51ef1f31c5f7e4',
             'ids': {'x': 'tY_a0e4015c066c1a73e43c6e7c4777abdeadb9f', 'y': 'pg_7d1eecc7838558a4c1bf9584d68a487791c45'},
             'x': 1,
             'y': 2}
        self.assertEqual(a.asdict, d)

    def test_illdefined_function(self):
        with pytest.raises(DependenceException):
            Ø >> {"x": 5} >> (lambda y: {"x": 5})
        with pytest.raises(NoInputException):
            Ø >> {"x": 5} >> (lambda: {"x": 5})

    def test_setitem_value(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 4
        d["z"] = 5
        self.assertEqual(
            """{
    "id": "Pd_7f559308b2f3bf28c9dfd54cf6ba43b636504",
    "ids": "WB_e55a47230d67db81bcc1aecde8f1b950282cd... +1 ...1U_fdd682399a475d5365aeb336044f7b4270977",
    "x": 3,
    "y": 4,
    "z": 5
}""",
            str(d),
        )

    def test_setitem_function(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}

        self.assertEqual(
            """{
    "id": "dq32pdZalIcM-fc5ZX1PZjUhNSpadBnjS7VNt6Mg",
    "ids": "m3S-qN-WiH188lwxKIguTF.2YniadBnjS7VNt6Mg... +1 ...0U_e2a86ff72e226d5365aea336044f7b4270977",
    "z": "→(x y)",
    "x": 3,
    "y": 5
}""",
            str(d),
        )
        self.assertEqual(d.z, 15)

    def test_setitem_overwrite_value(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}
        id = d.id
        self.assertEqual(id, d.id)

        # Overwrite same value.
        d.show()
        d["y"] = 5
        d.show()
        self.assertEqual(id, d.id)

        # Repeate same overwrite.
        d["y"] = 5
        self.assertEqual(id, d.id)

        # Overwrite other value.
        d["y"] = 6
        self.assertNotEqual(id, d.id)

    def test_rshift(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}
        self.assertEqual(
            """{
    "id": "dq32pdZalIcM-fc5ZX1PZjUhNSpadBnjS7VNt6Mg",
    "ids": "m3S-qN-WiH188lwxKIguTF.2YniadBnjS7VNt6Mg... +1 ...0U_e2a86ff72e226d5365aea336044f7b4270977",
    "z": "→(x y)",
    "x": 3,
    "y": 5
}""",
            str(d),
        )
        self.assertEqual(15, d.z)
        with pytest.raises(OverwriteException):
            d >>= {"z": 5}

    def test_overwrite(self):
        a = ldict(x=3)
        # a.show()
        # (a >> {"x": 3}).show()
        # self.assertEqual(a.idc, (a >> {"x": 3}).idc)  # overwrite
        b = ldict(y=4, x=3)
        a >>= {"y": 4}
        self.assertEqual(b.idc, a.idc)  # new value
        with pytest.raises(OverwriteException):
            self.assertNotEqual(a, a >> {"x": 3})

    def test_setitem_overwrite_function(self):
        d = ldict()
        d["x"] = 1
        d["y"] = 2
        d["z"] = 3

        # Apply some function.
        old = d
        d >>= lambda x, y, z: {"z": x + y * z}  # 7
        self.assertNotEqual(old, d)

        # Reapply same function.
        old = d
        d >>= lambda x, y, z: {"z": x + y * z}  # 15
        self.assertNotEqual(old, d)

        # Reapply same function.
        old = d
        d >>= lambda x, y, z: {"z": x + y * z}  # 31
        self.assertNotEqual(old, d)
        self.assertEqual(31, d.z)

        def f(x):
            return {"z": x + 2}

        a = Ø >> {"x": 1, "y": 2} >> f
        b = a >> (lambda x: {"z": x ** 2})
        self.assertNotEqual(a, b)
        self.assertNotEqual(a.ids["z"], b.ids["z"])
        self.assertEqual(a.ids["x"], b.ids["x"])
        self.assertEqual(a.ids["y"], b.ids["y"])

    def test_getitem(self):
        d = Ø >> {"x": 0}
        with pytest.raises(WrongKeyType):
            _ = d[1]
        with pytest.raises(KeyError):
            _ = d["1"]

    def test_delitem(self):
        d = Ø >> {"x": 0}
        with pytest.raises(WrongKeyType):
            del d[1]
        with pytest.raises(KeyError):
            del d["1"]
        with pytest.raises(ReadOnlyLdict):
            d["d"] = d
            del d.d["x"]

    def test_setitem(self):
        d = Ø >> {"x": 0}
        with pytest.raises(WrongKeyType):
            d[1] = 1

        d = Ø >> {"d": d}
        with pytest.raises(ReadOnlyLdict):
            d["d"]["x"] = 5

        T = namedtuple("T", "hosh")
        h = d.hosh
        t = T(d.hosh)
        d["t"] = t
        self.assertEqual(d.hosh, h * h)
