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
#
from random import Random
from typing import Dict, TypeVar, Union, Callable

from ldict.core.base import AbstractMutableLazyDict, AbstractLazyDict
from ldict.exception import WrongKeyType
from ldict.frozenlazydict import FrozenLazyDict
from ldict.parameter.functionspace import FunctionSpace
from ldict.parameter.let import AbstractLet

VT = TypeVar("VT")


class Ldict(AbstractMutableLazyDict):
    """Mutable lazy dict for serializable (picklable) pairs str->value

    Metafields like '_history' and '_code' can have Ellipsis ('...') as a placeholder
    to be automatically filled.

    >>> from ldict import ldict
    >>> ldict()
    {}
    >>> d = ldict(x=5, y=3)
    >>> d
    {
        "x": 5,
        "y": 3
    }
    >>> d["y"]
    3
    >>> ldict(x=123123, y=88)
    {
        "x": 123123,
        "y": 88
    }
    >>> ldict(y=88, x=123123)
    {
        "y": 88,
        "x": 123123
    }
    >>> d = ldict(x=123123, y=88)
    >>> e = d >> (lambda x: {"z": x**2}) >> (lambda x,y: {"w": x/y})
    >>> e
    {
        "x": 123123,
        "y": 88,
        "z": "→(x)",
        "w": "→(x y)"
    }
    >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x, y: {"w": x/y})
    >>> b = d >> (lambda x, y: {"w": x/y}) >> (lambda x: {"z": x**2})
    >>> dic = d.asdict  # Converting to dict
    >>> dic
    {'x': 123123, 'y': 88}
    >>> d2 = ldict(dic)  # Reconstructing from a dict
    >>> print(d2)
    {
        "x": 123123,
        "y": 88
    }
    >>> from ldict import empty
    >>> d = empty >> {"x": "more content"}
    >>> d
    {
        "x": "more content"
    }
    >>> def g(x):
    ...     return {"y": x**2, "_meta1": 0, "_history": Ellipsis, "_code": ...}
    >>> g.metadata = {"name": "squared", "description": "Some text."}
    >>> ldict(x=5) >> g
    {
        "x": 5,
        "y": "→(x)",
        "_meta1": "→(x)",
        "_code": "def f(x):\\nreturn {'y':x ** 2,  '_meta1':0,  '_history':Ellipsis,  '_code':...}",
        "_history": {
            "0": {
                "name": "squared",
                "description": "Some text."
            }
        }
    }
    >>> g.metadata = {"id": "9bab63dea3289def97aefde79b7aefde79b7c75d", "name": "squared", "description": "Some text."}
    >>> ldict(x=5) >> g
    {
        "x": 5,
        "y": "→(x)",
        "_meta1": "→(x)",
        "_code": "def f(x):\\nreturn {'y':x ** 2,  '_meta1':0,  '_history':Ellipsis,  '_code':...}",
        "_history": {
            "9bab63dea3289def97aefde79b7aefde79b7c75d": {
                "name": "squared",
                "description": "Some text."
            }
        }
    }
    >>> def g(inp=None, source=None, **kwargs):
    ...     res = kwargs[inp] ** 3
    ...     return {"w": res, "y": kwargs[source]**2, "_meta1": 0, "_history": Ellipsis, "_code": ...}
    >>> g.metadata = {"name": "squared using dynamic field", "description": "Some text."}
    >>> from ldict import let
    >>> (d := ldict(x=5) >> let(g, inp="x", source="x"))
    {
        "x": 5,
        "w": "→(inp source x)",
        "y": "→(inp source x)",
        "_meta1": "→(inp source x)",
        "_code": "def f(inp=None, source=None, **kwargs):\\nres = kwargs[inp] ** 3\\nreturn {'w':res,  'y':kwargs[source] ** 2,  '_meta1':0,  '_history':Ellipsis,  '_code':...}",
        "_history": {
            "0": {
                "name": "squared using dynamic field",
                "description": "Some text."
            }
        }
    }
    >>> d.w
    125
    >>> class MyCallableClass:
    ...     metadata = {
    ...         "name": "squared using dynamic field",
    ...         "description": "Some text.",
    ...         "input": {
    ...             "fields": ["a"],
    ...             "parameters": {"source": None, "target": None},
    ...             "dynamic": ["source"]
    ...         },
    ...         "output": {
    ...             "fields": ["y"],
    ...             "dynamic": ["target"],
    ...             "meta": ["_meta1"],
    ...             "auto": ["_history"]
    ...             }
    ...         }
    ...     def __call__(self, a, source=None, target=None, **kwargs):
    ...         return {"a2": a, target: kwargs[source]**a, "_meta1": 0}
    >>> f = MyCallableClass()
    >>> d = ldict(a=3, x=5) >> let(f, source="x", target="y")
    >>> d.evaluate()
    >>> d
    {
        "a": 3,
        "x": 5,
        "y": 125,
        "_meta1": 0,
        "_history": {
            "0": {
                "name": "squared using dynamic field",
                "description": "Some text."
            }
        }
    }
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, rnd=None, **kwargs):
        self.frozen: FrozenLazyDict = FrozenLazyDict(_dictionary or kwargs, rnd=rnd)

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        data = self.frozen.data.copy()
        del data[key]
        self.frozen = self.frozen.clone(data)

    def clone(self, data=None, rnd=None):
        """Same lazy content with (optional) new data or rnd object."""
        return self.__class__(self.frozen.data if data is None else data, rnd=rnd or self.rnd)

    def __rrshift__(self, left: Union[Random, Dict, Callable, FunctionSpace]):
        """
        >>> {"x":5} >> Ldict()
        {
            "x": 5
        }
        >>> (lambda x:x*2) >> Ldict()
        «λ × {}»
        >>> Random() >> Ldict()
        {}
        """
        clone = self.__class__()
        clone.frozen = left >> self.frozen
        return clone

    def __rshift__(self, other: Union[Dict, AbstractLazyDict, Callable, AbstractLet, FunctionSpace, Random]):
        """
        >>> d = Ldict(x=2) >> (lambda x: {"y": 2 * x})
        >>> d
        {
            "x": 2,
            "y": "→(x)"
        }
        """
        clone = self.__class__()
        clone.frozen = self.frozen >> other
        return clone
