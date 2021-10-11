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
from unittest import TestCase

import pytest

from ldict import ldict, Ø
from ldict.exception import DependenceException, NoInputException, WrongKeyType, ReadOnlyLdict


class TestLdict(TestCase):
    def test_identity(self):
        a = Ø >> {"x": 1, "y": 2}
        b = a >> Ø
        self.assertEqual(a, b)
        self.assertFalse(a == {"a": 3})
        self.assertNotEqual(a, {"a": 3})
        d = {'x': 1, 'y': 2}
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
    "x": 3,
    "y": 5,
    "z": "→(x y)"
}""",
            str(d),
        )
        self.assertEqual(d.z, 15)

    def test_setitem_overwrite_value(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}
        d.evaluate()
        self.assertEqual(d, {"x": 3, "y": 5, "z": 15})

        # Overwrite same value.
        d["y"] = 5
        self.assertEqual(d, {"x": 3, "y": 5, "z": 15})

        # Repeate same overwrite.
        d["y"] = 5
        self.assertEqual(d, {"x": 3, "y": 5, "z": 15})

        # Overwrite other value.
        d["y"] = 6
        self.assertNotEqual(d, {"x": 3, "y": 5, "z": 15})

    def test_rshift(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}
        self.assertEqual(
            """{
    "x": 3,
    "y": 5,
    "z": "→(x y)"
}""",
            str(d),
        )
        self.assertEqual(15, d.z)
        # with pytest.raises(OverwriteException):
        #     d >>= {"z": 5}

    def test_overwrite(self):
        a = ldict(x=3)
        self.assertEqual(a, a >> {"x": 3})  # overwrite
        a >>= {"y": 4}
        b = ldict(y=4, x=3)
        self.assertEqual(a, b)  # new value
        self.assertEqual(a, a >> {"x": 3})  # should differ for idict/cdict
        # with pytest.raises(OverwriteException):

    def test_setitem_overwrite_function(self):
        d = ldict()
        d["x"] = 1
        d["y"] = 2
        d["z"] = 3

        # Apply some function.
        old = d
        d >>= lambda x, y, z: {"z": x + y * z}  # 7
        self.assertNotEqual(old, d)
        self.assertEqual(d, {"x": 1, "y": 2, "z": 7})

        # Reapply same function.
        old = d
        d >>= lambda x, y, z: {"z": x + y * z}  # 15
        self.assertNotEqual(old, d)

        # Reapply same function.
        old = d
        d >>= lambda x, y, z: {"z": x + y * z}  # 31
        self.assertNotEqual(old, d)
        self.assertEqual(d, {"x": 1, "y": 2, "z": 31})

        def f(x):
            return {"z": x + 2}

        a = Ø >> {"x": 1, "y": 2} >> f
        b = a >> (lambda x: {"z": x ** 2})
        self.assertNotEqual(a, b)

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
        # with pytest.raises(ReadOnlyLdict):
        #     d["d"]["x"] = 5

        # T = namedtuple("T", "hosh")
