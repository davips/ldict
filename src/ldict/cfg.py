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
from dataclasses import dataclass
from random import Random
from typing import Union

from ldict import Ldict


@dataclass
class Ldict_cfg:
    ldict: Ldict
    config: dict
    rnd: Union[int, Random]

    def __rshift__(self, other):
        return self.ldict.__rshift__(other, self.config, self.rnd)


class cfg:
    def __init__(self, _rnd=None, _f=None, **kwargs):
        self.config = kwargs
        self.rnd = _rnd
        self.f = _f

    def __rshift__(self, other):
        return self.__class__(_rnd=self.rnd, _f=other, **self.config)

    def __rrshift__(self, other):
        from ldict import Ldict
        if not isinstance(other, dict):
            return NotImplemented
        return Ldict(other) >> self

    def __call__(self, rnd):
        return self.__class__(_rnd=rnd, _f=self.f, **self.config)
