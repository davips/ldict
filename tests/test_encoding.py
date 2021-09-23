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

import numpy as np

from ldict.serialization import value2blob


class Test(TestCase):
    def test_encode(self):
        self.assertEqual(
            b'{"_type":"<class \'numpy.ndarray\'>","dtype":"<U32","obj":[["0.33333333333'
            b'33333","1.25"],["19605347.64307615","text"]],"repr":"list"}',
            value2blob(np.array([[1 / 3, 5 / 4], [1.3 ** 64, "text"]]))
        )
