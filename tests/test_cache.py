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
#

from unittest import TestCase

from ldict import Ø
from ldict.config import setcache


class Test(TestCase):
    def test_cache(self):
        c = [0]

        def f(x):
            c[0] += 1
            return {"z": x + 2}

        setcache({})
        a = Ø >> {"x": 1, "y": 2} >> f ^ Ø
        self.assertEqual(0, c[0])
        self.assertEqual(1, a.x)
        self.assertEqual(0, c[0])
        self.assertEqual(2, a.y)
        self.assertEqual(0, c[0])
        self.assertEqual(3, a.z)
        self.assertEqual(1, c[0])
        self.assertEqual(3, a.z)
        self.assertEqual(1, c[0])

        c = [0]
        a = Ø >> {"x": 1, "y": 2} >> f ^ Ø
        self.assertEqual(0, c[0])
        self.assertEqual(3, a.z)
        self.assertEqual(0, c[0])

        a = Ø >> {"x": 1, "y": 2} >> f ^ Ø
        a >>= lambda z: {"z": z ** 2}
        self.assertEqual(9, a.z)
