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
        78297399190853865925546422718430264658855010523272162045457933175107322571720
        """
        return self.hosh.n

    @property
    def id(self):
        """
        Usage:

        >>> from ldict import ldict
        >>> ldict(x=134124).id
        '000000000000000000000aQqMuGtzigXKY9vs4vME6FPSHKoBxSJXSG4.IDSRKL8'
        >>> ldict(x=134124).ids
        {'x': '000000000000000000000aQqMuGtzigXKY9vs4vME6FPSHKoBxSJXSG4.IDSRKL8'}
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
            "id": "000000000000000000000cBXR5qArL1WVYOn7MW0MWyWhPWP31DmatnNd5soVRK0",
            "ids": {
                "x": "000000000000000000000aQqMuGtzigXKY9vs4vME6FPSHKoBxSJXSG4.IDSRKL8",
                "y": "0000000000000000000001Nx4CM6UsN0b0ETHIqg8ER6r8cqtvNh1mJIdoQy3kRR"
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
        [0, 0, 12473495331365790899, 7728865973021107401, 8212075338224970119, 6157470389993991581]
        >>> (a + b).cells
        [0, 0, 16031506638198821588, 13834746703073065004, 4696393870013716036, 6637745325376246119]
        >>> b = a + ldict(y=134124)
        >>> b.cells
        [0, 0, 16031506638198821588, 13834746703073065004, 4696393870013716036, 6637745325376246119]
        >>> f = lambda x: {'z': x ** 2}
        >>> print(b >> f)
        {
            "id": "pfwOevvOc0THi7b1R4kjIeBw1RzBLiLT3uxe.T0Cob2a9xr56v1mMJIIvBjUkNKm",
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
        ('000000000000000000000aQqMuGtzigXKY9vs4vME6FPSHKoBxSJXSG4.IDSRKL8', '0000000000000000000008RYrX8XDiNbFnEv9cJZy-pTw2nSHxy64stPR602KmI1')
        >>> print(a + b)
        {
            "id": "0000000000000000000003GncpPpaB5PojN-BhdJSHHHmK6fh4aZ3j7UQODURT5o",
            "ids": "<1 hidden ids>",
            "x": 134124,
            "y": 542542
        }
        >>> print(b + a)
        {
            "id": "0000000000000000000003GncpPpaB5PojN-BhdJSHHHmK6fh4aZ3j7UQODURT5o",
            "ids": "<1 hidden ids>",
            "y": 542542,
            "x": 134124
        }
        >>> print(b + a + b)
        {
            "id": "0000000000000000000003GncpPpaB5PojN-BhdJSHHHmK6fh4aZ3j7UQODURT5o",
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

        obj = ldict()
        # mutability WARNING: any attempt to inplace update nested structures will be disastrous, e.g.: d.d["x"] = 5
        # TODO: solution: freeze ldict when inserting, so that it cannot mutate anymore (deletion/insertion/update)
        #   It can be a wrapper class around _set_ and _del_
        obj.data = self.data.copy()
        obj.hoshes = self.hoshes.copy()
        obj.hosh = self.hosh
        obj.previous = self.previous.copy()
        obj.blobs = self.blobs.copy()
        obj.keepblob = self.keepblob
        obj.version = self.version
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
            "id": "000000000000000000000eqEFMZGUZzQFTmxCZxEnDEJHiWcdZc1I4.oNUufZzv9",
            "ids": "<1 hidden id>",
            "x": 123
        }
        >>> b = ldict(y="some text")
        >>> print(b)
        {
            "id": "0000000000000000000004uDaFL.-o9CHFrbEUsuhPnJHDTFe5Uoz746KCdo24Om",
            "ids": "<1 hidden id>",
            "y": "some text"
        }
        >>> b.update(a)
        >>> print(b)
        {
            "id": "0000000000000000000002VfQqJGTlN7lwNJfR-6l1ErmWNRs3SzhY3vwuHDhpYF",
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
        kwds.update(other)
        for field, value in kwds.items():
            if field not in ["id", "ids"]:
                self[field] = value
