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

from ldict import empty, let
from ldict.core.inspection import extract_input, extract_dictstr, extract_returnstr, extract_body
from ldict.core.ldict_ import Ldict
from ldict.core.rshift import list2progression
from ldict.exception import NoInputException, BadOutput, InconsistentLange, MultipleDicts, NoReturnException


class Test(TestCase):
    def test_input_fields(self):
        with pytest.raises(NoInputException):
            extract_input(lambda: 3)
        f = lambda **kwargs: {"x": 3}
        with pytest.raises(NoInputException):
            extract_input(f)

    def test_output_fields(self):
        def f(x):
            pass

        with pytest.raises(NoReturnException):
            extract_dictstr(extract_returnstr("".join(extract_body(f))))

        def f(x):
            return {"x": 1}, {"y": 2}

        with pytest.raises(MultipleDicts):
            extract_dictstr(extract_returnstr("".join(extract_body(f))))

        def f(x):
            return 0

        with pytest.raises(BadOutput):
            extract_dictstr(extract_returnstr("".join(extract_body(f))))

    def test_application(self):
        with pytest.raises(BadOutput):
            _ = empty >> {"x": 2} >> (lambda x: 0)

    def test_list2progression(self):
        with pytest.raises(InconsistentLange):
            list2progression([1, 2, 5, ..., 9])

    def test_dill(self):
        def f(input="a", output="b", **kwargs):
            return {output: kwargs[input], "_history": ..., "_function": ...}

        f.metadata = {"id": "fffffff----------------------------fffff",
                      "name": "f",
                      "description": "Copy.",
                      "code": ...,
                      "parameters": ...,
                      "function": ...}
        d = Ldict(a=5) >> let(f, output="b")
        self.assertEqual(str(d), """{
    "a": 5,
    "b": "→(input output a)",
    "_history": {
        "fffffff----------------------------fffff": {
            "name": "f",
            "description": "Copy.",
            "code": "def f(input='a', output='b', **kwargs):\\nreturn {output: kwargs[input], '_history': ..., '_function': ...}",
            "parameters": {
                "input": "a",
                "output": "b"
            }
        }
    },
    "_function": "b\\"\\\\x80\\\\x05\\\\x95\\\\x18\\\\x02\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x8c\\\\ndill._dill\\\\x94\\\\x8c\\\\x10_create_function\\\\x94\\\\x93\\\\x94(h\\\\x00\\\\x8c\\\\x0c_create_code\\\\x94\\\\x93\\\\x94(K\\\\x02K\\\\x00K\\\\x00K\\\\x03K\\\\x06K[C\\\\x14|\\\\x01|\\\\x02|\\\\x00\\\\x19\\\\x00d\\\\x01d\\\\x02d\\\\x03d\\\\x02i\\\\x03S\\\\x00\\\\x94(N\\\\x8c\\\\x08_history\\\\x94h\\\\x00\\\\x8c\\\\n_eval_repr\\\\x94\\\\x93\\\\x94\\\\x8c\\\\x08Ellipsis\\\\x94\\\\x85\\\\x94R\\\\x94\\\\x8c\\\\t_function\\\\x94t\\\\x94)\\\\x8c\\\\x05input\\\\x94\\\\x8c\\\\x06output\\\\x94\\\\x8c\\\\x06kwargs\\\\x94\\\\x87\\\\x94\\\\x8c)/home/davi/git/ldict/tests/test_rshift.py\\\\x94\\\\x8c\\\\x01f\\\\x94KEC\\\\x02\\\\x00\\\\x01\\\\x94))t\\\\x94R\\\\x94ctests.test_rshift\\\\n__dict__\\\\nh\\\\x13\\\\x8c\\\\x01a\\\\x94\\\\x8c\\\\x01b\\\\x94\\\\x86\\\\x94N}\\\\x94\\\\x8c\\\\x08metadata\\\\x94}\\\\x94(\\\\x8c\\\\x02id\\\\x94\\\\x8c(fffffff----------------------------fffff\\\\x94\\\\x8c\\\\x04name\\\\x94h\\\\x13\\\\x8c\\\\x0bdescription\\\\x94\\\\x8c\\\\x05Copy.\\\\x94\\\\x8c\\\\x04code\\\\x94\\\\x8cidef f(input='a', output='b', **kwargs):\\\\nreturn {output: kwargs[input], '_history': ..., '_function': ...}\\\\x94\\\\x8c\\\\nparameters\\\\x94}\\\\x94(h\\\\x0eh\\\\x17h\\\\x0fh\\\\x18u\\\\x8c\\\\x08function\\\\x94h\\\\x0busNt\\\\x94R\\\\x94.\\""
}""")
