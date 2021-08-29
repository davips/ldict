import json
import re
from typing import Iterator, Iterable, TypeVar, Union
from typing import TYPE_CHECKING

from garoupa import Hosh

from ldict_modules.lazy import Lazy

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
        [0, 0, 1046869178, 2442989982, 1777475881, 2847007990]
        >>> (a + b).cells
        [0, 0, 2621165707, 3945024901, 14724739, 3837620993]
        >>> b = a + ldict(y=134124)
        >>> b.cells
        [0, 0, 2621165707, 3945024901, 14724739, 3837620993]
        >>> f = lambda x: {'z': x ** 2}
        >>> print(b >> f)
        {
            "id": "b6iBJUI-6bBh0amXQXuMrvuu.unh4vab",
            "ids": "b6iBJUI-6bCQNdkB41irvRsir15H..4d... +2 ...00000000001tRtLbSvZqM9ldD68RaQ.A",
            "z": "→(x)",
            "x": 134124,
            "y": 134124
        }
        """
        return self.hosh.cells

    def __str__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if isinstance(v, Lazy):
                dic[k] = str(v)
        if not all:
            if len(self.ids) < 3:
                dic["ids"] = " ".join(self.ids.values())
            else:
                ids = list(self.ids.values())
                dic["ids"] = f"{ids[0]}... +{(len(self) - 1) // 2} ...{ids[-1]}"
        return json.dumps(dic, indent=4, ensure_ascii=False)

    def __repr__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if isinstance(v, Lazy):
                dic[k] = str(v)
        if not all:
            dic["ids"] = "<1 hidden id>" if len(dic["ids"]) == 1 else f"<{(len(self) - 1) // 2} hidden ids>"
        txt = json.dumps(dic, indent=4, ensure_ascii=False)
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
        ('00000000000-pviSWqeWNg6K8SBoxnz5', '00000000002mKYOzJxMGOXt0d00OFKXG')
        >>> print(a + b)
        {
            "id": "00000000003l8s5pDX.BDHzKlOybb6wj",
            "ids": "00000000000-pviSWqeWNg6K8SBoxnz5 00000000002mKYOzJxMGOXt0d00OFKXG",
            "x": 134124,
            "y": 542542
        }
        >>> print(b + a)
        {
            "id": "00000000003l8s5pDX.BDHzKlOybb6wj",
            "ids": "00000000002mKYOzJxMGOXt0d00OFKXG 00000000000-pviSWqeWNg6K8SBoxnz5",
            "y": 542542,
            "x": 134124
        }
        >>> print(b + a + b)
        {
            "id": "00000000003l8s5pDX.BDHzKlOybb6wj",
            "ids": "00000000002mKYOzJxMGOXt0d00OFKXG 00000000000-pviSWqeWNg6K8SBoxnz5",
            "y": 542542,
            "x": 134124
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
        return hash(self.hosh)

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
            "id": "00000000001J3NH7RxPk1KaXpcKTZKyn",
            "ids": "00000000001J3NH7RxPk1KaXpcKTZKyn",
            "x": 123
        }
        >>> b = ldict(y="some text")
        >>> print(b)
        {
            "id": "00000000001MBkeRJxvTONG7hkCFgzDd",
            "ids": "00000000001MBkeRJxvTONG7hkCFgzDd",
            "y": "some text"
        }
        >>> b.update(a)
        >>> print(b)
        {
            "id": "00000000003tF5VZz3jbQvR2Gxhxei9F",
            "ids": "00000000001MBkeRJxvTONG7hkCFgzDd 00000000001J3NH7RxPk1KaXpcKTZKyn",
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
            "id": "oA4Wx.uyOR.dKno71my3KuC2mvbni-u4",
            "ids": {
                "y": "oA4Wx.uyOS2b7bDEjIIEgYr5d8E6FQis",
                "x": "000000000012DbMaJFRs3dca34FbGven"
            },
            "y": "→(x)",
            "x": 3
        }
        >>> a.evaluate()
        >>> a.show(colored=False)
        {
            "id": "oA4Wx.uyOR.dKno71my3KuC2mvbni-u4",
            "ids": {
                "y": "oA4Wx.uyOS2b7bDEjIIEgYr5d8E6FQis",
                "x": "000000000012DbMaJFRs3dca34FbGven"
            },
            "y": 5,
            "x": 3
        }
        >>> a = ldict(x=3) >> (lambda x: {"x": x+2})
        >>> a.show(colored=False)
        {
            "id": "kRDDYQ1V4KvywzYQIuFcWItzGl.BTxHc",
            "ids": {
                "x": "000000000012DbMaJFRs3dca34FbGven"
            },
            "x": "→(x)"
        }
        >>> a.x
        5

        Returns
        -------

        """
        for field in self:
            self[field]
