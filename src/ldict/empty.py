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
from typing import Callable, Dict, Union

from ldict.core.ldict_ import Ldict
from ldict.frozenlazydict import FrozenLazyDict
from ldict.parameter.functionspace import FunctionSpace


class Empty(FrozenLazyDict):
    def __init__(self):
        super().__init__()

    def __rshift__(self, other: Union[Dict, Callable, FunctionSpace], config={}):
        from ldict.parameter.let import Let
        if callable(other):
            return FunctionSpace(other)
        if isinstance(other, (Let, Ldict)):
            return other
        if isinstance(other, dict):
            return Ldict(other)
        return NotImplemented
