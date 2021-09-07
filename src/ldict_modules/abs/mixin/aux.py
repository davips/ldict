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
