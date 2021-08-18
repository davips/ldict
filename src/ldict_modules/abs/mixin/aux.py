import json
import re
from typing import Iterator, Iterable, TypeVar, Union
from typing import TYPE_CHECKING

from garoupa import Hosh

if TYPE_CHECKING:
    from ldict import Ldict

VT = TypeVar("VT")


class Aux:
    hosh: Hosh
    hoshes: dict
    data: dict
    keepblob: bool
    version: str

    @property
    def n(self):
        """
        Usage:

        >>> from ldict import ldict
        >>> ldict(x=134124).n
        242961611356438631232947123073942258732
        """
        return self.hosh.n

    @property
    def id(self):
        """
        Usage:

        >>> from ldict import ldict
        >>> ldict(x=134124).id
        '00000000002SObhaIF6dmbIhF.sNVUgI'
        >>> ldict(x=134124).ids
        {'x': '00000000002SObhaIF6dmbIhF.sNVUgI'}
        """
        return self.hosh.id

    @property
    def idc(self):
        """Colored id"""
        return self.hosh.idc

    @property
    def ids(self):
        return self.data["ids"]

    @property
    def all(self):
        """
        Usage:

        >>> from ldict import ldict
        >>> out = ldict(x=134124, y= 56).all
        >>> print(ansi_escape.sub('', out))  # doctest: +SKIP
        {
            "id": "LI2jBaxgZwh8khoYlfAYikEI8gnGnN5NX2h6kBwL6v2",
            "x": 134124,
            "id_x": "MO72GzebQLg1Q6EfBqPlpor9I5P7XXDByDrXsj9kdSS",
            "y": 56,
            "id_y": "xbfZfXwFFza8UwbSM6HM5ig8VqYmwXewLkX7LW7SAV6"
        }
        """
        return self.__repr__(all=True)

    def show(self, colored=True):
        """
        Usage:

        >>> from ldict import ldict
        >>> ldict(x=134124, y= 56).show(colored=False)
        {
            "id": "00000000000.jlz3OeWf68UZ-Wfrjhn3",
            "ids": {
                "x": "00000000002SObhaIF6dmbIhF.sNVUgI",
                "y": "000000000028xahB5BQ2ltcIkrCFppg3"
            },
            "x": 134124,
            "y": 56
        }
        """
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return print(self.all if colored else ansi_escape.sub("", self.all))

    @property
    def cells(self):
        """
        For new untransformed data, it is always the identity permutation.
        Usage:

        >>> from ldict import ldict
        >>> a = ldict(x=134124)
        >>> b = ldict(y=134124)
        >>> a.cells
        [0, 0, 3066606677, 1750343202, 1099825332, 2306253791]
        >>> (a + b).cells
        [0, 0, 23189221, 15893371, 2300255245, 881945888]
        >>> b = a + ldict(y=134124)
        >>> b.cells
        [0, 0, 23189221, 15893371, 2300255245, 881945888]
        >>> f = lambda x: {'z': x ** 2}
        >>> print(b >> f)
        {
            "id": "6gpauRwNufp-ZK.NT4goJV9C4AWWqETT",
            "ids": "<2 hidden ids>",
            "z": "<unevaluated lazy field>",
            "x": 134124,
            "y": 134124
        }
        """
        return self.hosh.cells

    def __str__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if callable(v):
                dic[k] = "<unevaluated lazy field>"
        if not all:
            dic["ids"] = "<1 hidden id>" if len(dic["ids"]) == 1 else f"<{(len(self) - 1) // 2} hidden ids>"
        return json.dumps(dic, indent=4)

    def __repr__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if callable(v):
                dic[k] = "<unevaluated lazy field>"
        if not all:
            dic["ids"] = "<1 hidden id>" if len(dic["ids"]) == 1 else f"<{(len(self) - 1) // 2} hidden ids>"
        txt = json.dumps(dic, indent=4)
        for k, v in dic.items():
            if k == "id":
                txt = txt.replace(dic[k], self.hosh.idc)
        if all:
            for k, v in self.hoshes.items():
                txt = txt.replace(v.id, v.idc)  # REMINDER: workaround to avoid json messing with colors
        return txt

    def __add__(self, other):
        """
        Usage:

        >>> from ldict import ldict
        >>> a = ldict(x=134124)
        >>> b = ldict(y=542542)
        >>> a.id, b.id
        ('00000000002SObhaIF6dmbIhF.sNVUgI', '00000000003mpDOELy5K.VwDZ9Vyn2AW')
        >>> print(a + b)
        {
            "id": "00000000002dbP47sbbXMlcVDFakgWHx",
            "ids": "<1 hidden ids>",
            "x": 134124,
            "y": 542542
        }
        >>> print(b + a)
        {
            "id": "00000000002dbP47sbbXMlcVDFakgWHx",
            "ids": "<1 hidden ids>",
            "y": 542542,
            "x": 134124
        }
        >>> print(b + a + b)
        {
            "id": "00000000002dbP47sbbXMlcVDFakgWHx",
            "ids": "<1 hidden ids>",
            "x": 134124,
            "y": 542542
        }
        """

        from ldict import ldict

        new = ldict(self)
        new.update(other)
        return new

    def copy(self):
        from ldict import ldict

        obj = ldict(keepblob=self.keepblob, version=self.version)
        # mutability WARNING: any attempt to inplace update nested structures will be disastrous, e.g.: d.d["x"] = 5
        # TODO: solution: freeze ldict if being inserted as a value in other ldict, so that it cannot mutate anymore (deletion/insertion/update)
        #   It can be a wrapper class around _set_ and _del_
        obj.data = self.data.copy()
        obj.hoshes = self.hoshes.copy()
        # obj.hashes = self.hashes.copy()  #TODO
        obj.hosh = self.hosh
        obj.previous = self.previous.copy()
        obj.blobs = self.blobs.copy()
        return obj

    @property
    def hex(self):
        return hex(self.n)[2:]

    def __hash__(self):
        return self.n

    def __eq__(self, other):
        from ldict import Ldict

        if isinstance(other, Ldict):
            return self.n == other.n
        return NotImplemented

    def __ne__(self, other):
        return self.hosh != other.hosh

    def __contains__(self, field: str) -> bool:
        return field in self.data

    def __getattr__(self, item):
        if item in self:
            return self[item]
        return self.__getattribute__(item)

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.data)

    @classmethod
    def fromkeys(cls, iterable: Iterable[str], value: VT) -> "Union[Ldict, Aux]":
        """Create a new dictionary with keys from `iterable` and values set to `value`.

        Args:
            iterable: A collection of keys.
            value: The default value. It defaults to None.
            All of the values refer to just a single instance,
            so it generally doesn’t make sense for value to be a mutable object such as an empty list.
            To get distinct values, use a dict comprehension instead.

        Returns:
            A new instance of Dict.
        """
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def keys(self):
        yield from self.data.keys()

    def update(self, other=(), /, **kwds):
        """Update the dictionary with the key/value pairs from other, overwriting existing keys.
        Usage:

        >>> from ldict import ldict
        >>> a = ldict(x=123)
        >>> print(a)
        {
            "id": "00000000002stN2crXIrINutqB4rNGWr",
            "ids": "<1 hidden id>",
            "x": 123
        }
        >>> b = ldict(y="some text")
        >>> print(b)
        {
            "id": "000000000021j-B-Pd-.ZBcWw9a6sVoI",
            "ids": "<1 hidden id>",
            "y": "some text"
        }
        >>> b.update(a)
        >>> print(b)
        {
            "id": "00000000000tNLEvf9Hr4SHnXdqyeA9r",
            "ids": "<1 hidden ids>",
            "y": "some text",
            "x": 123
        }
        """
        from ldict import Ldict

        if isinstance(other, Ldict):
            if self.version != other.version:
                raise Exception("Different versions:", self.version, other.version)
            self.keepblob = self.keepblob or other.keepblob
            self.blobs.update(other.blobs)
            other.evaluate()
        kwds.update(other)
        for field, value in kwds.items():
            if field not in ["id", "ids"]:
                self[field] = value

    def evaluate(self):
        """
        Usage:

        >>> from ldict import ldict
        >>> a = ldict(x=3) >> (lambda x: {"y": x+2})
        >>> a.show(colored=False)
        {
            "id": "32GJlU0bICVvZ0.L1cS8HJ5Bin47kG6u",
            "ids": {
                "y": "32GJlU0bICW9eJIGonjBPBnvwjsRY6yo",
                "x": "00000000003mKjiNERyzq0vnvE.VYU4H"
            },
            "y": "<unevaluated lazy field>",
            "x": 3
        }
        >>> a.evaluate()
        >>> a.show(colored=False)
        {
            "id": "32GJlU0bICVvZ0.L1cS8HJ5Bin47kG6u",
            "ids": {
                "y": "32GJlU0bICW9eJIGonjBPBnvwjsRY6yo",
                "x": "00000000003mKjiNERyzq0vnvE.VYU4H"
            },
            "y": 5,
            "x": 3
        }
        >>> a = ldict(x=3) >> (lambda x: {"x": x+2})
        >>> a.show(colored=False)
        {
            "id": "j5BZ5LZL6Ty4--z8vyNKNzAW.iJa-Hc6",
            "ids": {
                "x": "00000000003mKjiNERyzq0vnvE.VYU4H"
            },
            "x": 3
        }
        >>> a.x
        5

        Returns
        -------

        """
        for field in self:
            self[field]

