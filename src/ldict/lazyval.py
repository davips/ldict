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


class LazyVal:
    """
    >>> lazies = []
    >>> f = lambda l: {"y":1, "z":2}
    >>> deps = {"l":LazyVal("y", f, {"l":0}, None)}
    >>> a = LazyVal("y", f, deps, lazies)
    >>> b = LazyVal("z", f, deps, lazies)
    >>> lazies.extend([a, b])
    >>> a
    →(l→(l))
    >>> b
    →(l→(l))
    >>> a()
    1
    >>> a
    1
    >>> b
    2
    """

    def __init__(self, field, f, deps, lazies):
        self.field = field
        self.f = f
        self.deps = deps
        self.lazies = lazies
        self.result = None

    def __call__(self, *args, **kwargs):
        if self.result is None:
            for k, v in self.deps.items():
                if isinstance(v, LazyVal):
                    self.deps[k] = v()
            ret = self.f(**self.deps)
            if self.lazies is None:
                self.result = ret
            else:
                self.result = ret[self.field]
                for lazy in self.lazies:
                    lazy.result = ret[lazy.field]
        return self.result

    def __repr__(self):
        if self.result is None:
            dic = {}
            for k, v in self.deps.items():
                dic[k] = v if isinstance(v, LazyVal) else ""
            return f"→({' '.join([f'{k}{v}' for k, v in dic.items()])})"
        return str(self.result)
