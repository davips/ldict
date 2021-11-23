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

from ldict.parameter.abslet import AbstractLet
from ldict.parameter.functionspace import FunctionSpace


class lLet(AbstractLet):
    """
    Set values or sampling intervals for parameterized functions

    >>> from ldict import ldict, let
    >>> f = lambda x,y, a=[-1,-0.9,-0.8,...,1]: {"z": a*x + y}
    >>> f_a = let(f, a=0)
    >>> f_a
    λ{'a': 0}
    >>> d = ldict(x=5,y=7)
    >>> d2 = d >> f_a
    >>> d2
    {
        "x": 5,
        "y": 7,
        "z": "→(a x y)"
    }
    >>> d2.evaluate()
    >>> d2
    {
        "x": 5,
        "y": 7,
        "z": 7
    }
    >>> from random import Random
    >>> d2 = d >> Random(0) >> let(f, a=[8,9])
    >>> d2
    {
        "x": 5,
        "y": 7,
        "z": "→(a x y)"
    }
    >>> d2.evaluate()
    >>> d2
    {
        "x": 5,
        "y": 7,
        "z": 52
    }
    >>> let(f, a=5) >> {"x": 5, "y": 7}
    «λ{'a': 5} × {'x': 5, 'y': 7}»
    >>> ldict({"x": 5, "y": 7}) >> let(f, a=5)
    {
        "x": 5,
        "y": 7,
        "z": "→(a x y)"
    }
    >>> let(f, a=5) >> ldict({"x": 5, "y": 7})
    «λ{'a': 5} × {
        "x": 5,
        "y": 7
    }»
    >>> from random import Random
    >>> let(f, a=5) >> ["mycache"]  # Cache implemented in package 'cdict'.
    «λ{'a': 5} × ^»
    >>> from ldict.parameter.functionspace import FunctionSpace
    >>> let(f, a=5) >> FunctionSpace()
    λ{'a': 5}
    >>> FunctionSpace() >> let(f, a=5)
    «λ{'a': 5}»
    >>> (lambda x: {"z": x*8}) >> let(f, a=5)
    «λ{} × λ{'a': 5}»
    >>> d = {"x":3, "y": 8} >> let(f, a=5)
    >>> d
    {
        "x": 3,
        "y": 8,
        "z": "→(a x y)"
    }
    >>> d.z
    23
    >>> d >>= Random(0) >> let(f, a=[1,2,3]) >> let(f, a=[9,8,7])
    >>> d
    {
        "x": 3,
        "y": 8,
        "z": "→(a x y)"
    }
    >>> d.z
    32
    """

    def __init__(self, f, **kwargs):
        from ldict.core.ldict_ import Ldict

        super().__init__(f, Ldict, **kwargs)
