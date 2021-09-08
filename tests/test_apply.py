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
from random import Random
from unittest import TestCase

import pytest

from garoupa import ø40
from ldict import ø
from ldict.apply import input_fields, output_fields, application
from ldict.exception import NoInputException, NoReturnException, BadOutput, FunctionETypeException


class Test(TestCase):
    def test_input_fields(self):
        with pytest.raises(NoInputException):
            input_fields(lambda: 3, {})

    def test_output_fields(self):
        def f(x):
            pass

        with pytest.raises(NoReturnException):
            output_fields(f)

        def f(x):
            return {"x": 1}, {"y": 2}

        with pytest.raises(BadOutput):
            output_fields(f)

        def f(x):
            return 0

        with pytest.raises(BadOutput):
            output_fields(f)

    def test_application(self):
        def f(x):
            return {"x³": x ** 3}

        f.hosh = ø40 * 2 ** 65
        with pytest.raises(FunctionETypeException):
            application(ø, ø, f, {}, Random())

        delattr(f, "hosh")
        with pytest.raises(BadOutput):
            _ = ø >> {"x": 2} >> f
