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

from ldict import ldict, ø
from ldict_modules.exception import FromØException, DependenceException, NoInputException


class TestLdict(TestCase):
    def test_identity(self):
        a = ø >> {"x": 1, "y": 2}
        b = a >> ø
        self.assertEqual(a, b)

    def test_illdefined_function(self):
        with pytest.raises(FromØException):
            ø >> (lambda y: {"x": 5})
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
    "id": "00000000001w6Ep1HQgaMx-d-i-4i1OB",
    "ids": "000000000012DbMaJFRs3dca34FbGven... +2 ...00000000002MOCZRpfJZZbdpTtxagqTj",
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
    "id": "jnBdalsrWotpNVXb1tp172EErX.uzBcj",
    "ids": "jnBdalsrWorPQrdwxvEp7mDAvY3V1YRZ... +2 ...00000000000zmiZwOjXbVbfdGeoJrdzK",
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
        self.assertEqual("jnBdalsrWotpNVXb1tp172EErX.uzBcj", d.id)

        # Repeate same overwrite.
        d["y"] = 5
        self.assertEqual("jnBdalsrWotpNVXb1tp172EErX.uzBcj", d.id)

        # Overwrite other value.
        d["y"] = 6
        self.assertEqual("jnBdalsrWor2AgxVe.vYvASzgdhOqgtP", d.id)

    def test_rshift(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}
        self.assertEqual(
            """{
    "id": "jnBdalsrWotpNVXb1tp172EErX.uzBcj",
    "ids": "jnBdalsrWorPQrdwxvEp7mDAvY3V1YRZ... +2 ...00000000000zmiZwOjXbVbfdGeoJrdzK",
    "z": "→(x y)",
    "x": 3,
    "y": 5
}""",
            str(d),
        )

        self.assertEqual(15, d.z)

    def test_overwrite(self):
        a = ldict(x=3)
        # a.show()
        # (a >> {"x": 3}).show()
        # self.assertEqual(a.idc, (a >> {"x": 3}).idc)  # overwrite
        b = ldict(y=4, x=3)
        a.show()
        a >>= {"y": 4}
        a.show()
        self.assertEqual(b.idc, a.idc)  # new value

        # self.assertNotEqual(a, a >> {"x": 3})
        # def f():
        #     a["x"] = 5

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


"""
        >>> d >>= {"y": 2}
        >>> d.show(colored=False)
        {
            "id": "0000000000000000000005ZAUVMzxwjwXbh7mLzet1L.rDnoCfw4gnGNFOvMzRW-",
            "ids": {
                "x": "000000000000000000000c3aop1df5AZXCRMY3yInQeUYccGQRclWo8TvfKPB4YT",
                "y": "0000000000000000000009WqwwLmiqGS.ArmqI0ypCV6vraJNpxBjfxWayMZI.iZ"
            },
            "x": 2,
            "y": 2
        }
        >>> d >>= (lambda x: {"x": x**2})
        >>> d.show(colored=False)
        {
            "id": "aMxJyzaP3pwUZmywZdR2Aal7WMRcOcoR6oAgBnvJcJ0j9sHBGGtBMV8XQNcx8vTQ",
            "ids": {
                "x": "000000000000000000000c3aop1df5AZXCRMY3yInQeUYccGQRclWo8TvfKPB4YT",
                "y": "0000000000000000000009WqwwLmiqGS.ArmqI0ypCV6vraJNpxBjfxWayMZI.iZ"
            },
            "x": 2,
            "y": 2
        }
"""

#         d = ldict(x=123123, y=88)
# d.show()
# e = d >> (lambda x, y: {"z": x ** 22, "w": x / y})


# TODO:
#   exception if function is not in G\H
#   all requirements from paper
