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
from abc import abstractmethod, ABC
from collections import UserDict
from random import Random
from typing import Dict, TypeVar

from ldict.exception import WrongKeyType

VT = TypeVar("VT")


class AbstractLazyDict(UserDict, Dict[str, VT]):
    rnd: Random

    @property
    @abstractmethod
    def asdict(self):
        raise NotImplementedError


class AbstractMutableLazyDict(AbstractLazyDict, ABC):
    rnd: Random
    frozen: AbstractLazyDict

    @property
    def rnd(self):
        return self.frozen.rnd

    @property
    def data(self):
        return self.frozen.data

    def __getitem__(self, item):
        return self.frozen[item]

    def __setitem__(self, key: str, value):
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        self.frozen >>= {key: value}
