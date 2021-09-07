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

from ldict import ldict, ø
from ldict_modules.exception import DependenceException, NoInputException, WrongKeyType, WrongValueType, ReadOnlyLdict, \
    OverwriteException


class TestLdict(TestCase):
    def test_identity(self):
        a = ø >> {"x": 1, "y": 2}
        b = a >> ø
        self.assertEqual(a, b)
        self.assertFalse(a == 123)
        self.assertNotEqual(a, 123)
        self.assertEqual(a.hosh.n % maxsize, hash(a))
        d = {'id': 'Tb_334cc16924a8bdc38205599e516203f9054c4',
             'ids': {'x': 'lv_56eec09cd869410b23dcb462b64fe26acc2a2', 'y': 'yI_a331070d4bcdde465f28ba37ba1310e928122'},
             'x': 1,
             'y': 2}
        self.assertEqual(a.asdict, d)

    def test_illdefined_function(self):
        with pytest.raises(DependenceException):
            ø >> {"x": 5} >> (lambda y: {"x": 5})
        with pytest.raises(NoInputException):
            ø >> {"x": 5} >> (lambda: {"x": 5})

    def test_setitem_value(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 4
        d["z"] = 5
        self.assertEqual(
            """{
    "id": "Eh_00710612d0ed177a866b2cf5e6fbdbc5b9bff",
    "ids": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002... +2 ...Vz_d467c65677734fad67e6de7cdba3ea368aae4",
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
    "id": "Yh6activ2aPNEtjkAeFtbIXZiZoadBnjS7VNt6Mg",
    "ids": "i9o-7w8EyntJ45qTLHzOyu33capadBnjS7VNt6Mg... +2 ...Uz_0af6d78f77734fad67e6de7cdba3ea368aae4",
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

        # Overwrite same value.
        d["y"] = 5
        self.assertEqual("Yh6activ2aPNEtjkAeFtbIXZiZoadBnjS7VNt6Mg", d.id)

        # Repeate same overwrite.
        d["y"] = 5
        self.assertEqual("Yh6activ2aPNEtjkAeFtbIXZiZoadBnjS7VNt6Mg", d.id)

        # Overwrite other value.
        d["y"] = 6
        self.assertEqual("qb0KHIpi2b06ikRW.fzJr5V1.rsadBnjS7VNt6Mg", d.id)

    def test_rshift(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}
        self.assertEqual(
            """{
    "id": "Yh6activ2aPNEtjkAeFtbIXZiZoadBnjS7VNt6Mg",
    "ids": "i9o-7w8EyntJ45qTLHzOyu33capadBnjS7VNt6Mg... +2 ...Uz_0af6d78f77734fad67e6de7cdba3ea368aae4",
    "z": "→(x y)",
    "x": 3,
    "y": 5
}""",
            str(d),
        )
        self.assertEqual(15, d.z)
        with pytest.raises(WrongValueType):
            d >>= {"z": lambda: None}
        with pytest.raises(OverwriteException):
            d >>= {"z": 5}
        with pytest.raises(WrongValueType):
            d >>= None

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

        a = ø >> {"x": 1, "y": 2} >> f
        b = a >> (lambda x: {"z": x ** 2})
        self.assertNotEqual(a, b)
        self.assertNotEqual(a.ids["z"], b.ids["z"])
        self.assertEqual(a.ids["x"], b.ids["x"])
        self.assertEqual(a.ids["y"], b.ids["y"])

    def test_getitem(self):
        d = ø >> {"x": 0}
        with pytest.raises(WrongKeyType):
            _ = d[1]
        with pytest.raises(KeyError):
            _ = d["1"]

    def test_delitem(self):
        d = ø >> {"x": 0}
        with pytest.raises(WrongKeyType):
            del d[1]
        with pytest.raises(KeyError):
            del d["1"]
        with pytest.raises(ReadOnlyLdict):
            d["d"] = d
            del d.d["x"]

    def test_setitem(self):
        d = ø >> {"x": 0}
        with pytest.raises(WrongKeyType):
            d[1] = 1
        with pytest.raises(WrongValueType):
            d["x"] = lambda x: x

        d = ø >> {"d": d}
        with pytest.raises(ReadOnlyLdict):
            d["d"]["x"] = 5

        T = namedtuple("T", "hosh")
        h = d.hosh
        t = T(d.hosh)
        d["t"] = t
        self.assertEqual(d.hosh, h * h)
