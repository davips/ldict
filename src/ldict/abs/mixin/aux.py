import json
import re
from typing import Iterator, Iterable, TypeVar, Union
from typing import TYPE_CHECKING

from garoupa import Hash

if TYPE_CHECKING:
    from ldict import Ldict

VT = TypeVar('VT')


class Aux:
    hash: Hash
    hashes: dict
    data: dict
    keepblob: bool

    @property
    def n(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124).n
        42705542750959941452191592945617646912015657253877602974646311981218661400576
        """
        return self.hash.n

    @property
    def id(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124).id
        'MO72GzebQLg1Q6EfBqPlpor9I5P7XXDByDrXsj9kdSS'
        """
        return self.hash.id

    @property
    def ids(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124).ids
        {'x': 'MO72GzebQLg1Q6EfBqPlpor9I5P7XXDByDrXsj9kdSS'}
        """
        return {f: h.id for f, h in self.hashes.items()}

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
            "id": "LI2jBaxgZwh8khoYlfAYikEI8gnGnN5NX2h6kBwL6v2",
            "x": 134124,
            "id_x": "MO72GzebQLg1Q6EfBqPlpor9I5P7XXDByDrXsj9kdSS",
            "y": 56,
            "id_y": "xbfZfXwFFza8UwbSM6HM5ig8VqYmwXewLkX7LW7SAV6"
        }
        """
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return print(self.all if colored else ansi_escape.sub("", self.all))

    @property
    def perm(self):
        """
        For new untransformed data, it is always the identity permutation.
        Usage:
        >>> from ldict import ldict
        >>> a = ldict(x=134124)
        >>> b = ldict(y=134124)
        >>> a.perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> (a + b).perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> b = a + ldict(y=134124)
        >>> b.perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> f = lambda x: {'z': x ** 2}
        >>> print(b >> f)
        {
            "id": "C17Mr4mTIkxhTyWav1AHAgcXYAVgFivx1aqnfvhHxng",
            "x": 134124,
            "y": 134124,
            "z": "<unevaluated lazy field>",
            "id_*": "<3 hidden fields>"
        }
        """
        return self.hash.perm

    def __str__(self, all=False):
        dic = self.data.copy()
        k = None
        for k, v in self.data.items():
            if not all and k.startswith("id_"):
                del dic[k]
            elif callable(v):
                dic[k] = "<unevaluated lazy field>"
        if not all:
            if len(self) == 3:
                dic[k] = "<hidden field>"
            elif len(self) > 3:
                dic["id_*"] = f"<{(len(self) - 1) // 2} hidden fields>"
        return json.dumps(dic, indent=4)

    def __repr__(self, all=False):
        dic = self.data.copy()
        k = None
        for k, v in self.data.items():
            if callable(v):
                dic[k] = "<unevaluated lazy field>"
            if not all and k.startswith("id_"):
                del dic[k]
        if not all:
            if len(self) == 3:
                dic[k] = f"<hidden field>"
            elif len(self) > 3:
                dic["id_*"] = f"<{(len(self) - 1) // 2} hidden fields>"
        txt = json.dumps(dic, indent=4)
        for k, v in dic.items():
            if k == "id":
                txt = txt.replace(dic[k], self.hash.idc)
            elif all and k.startswith("id_"):
                txt = txt.replace(dic[k], self.hashes[k[3:]].idc)
        return txt

    def __add__(self, other):
        """
        Usage:
        >>> from ldict import ldict
        >>> a = ldict(x=134124)
        >>> b = ldict(y=542542)
        >>> a.id, b.id
        ('MO72GzebQLg1Q6EfBqPlpor9I5P7XXDByDrXsj9kdSS', 'W7cGnj0REY7cd4sABgl63msGq30vtvVrxEoXrt64obY')
        >>> print(a + b)
        {
            "id": "sVjJ4if2etne3B6pNXArtbjQ88Q3RSj3vSg5kcFpS40",
            "x": 134124,
            "y": 542542,
            "id_*": "<2 hidden fields>"
        }
        """
        from ldict import ldict
        new = ldict(self)
        return new.update(other)

    def copy(self):
        from ldict import ldict
        return ldict(self)

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

    def update(self, other=(), /, **kwds) -> "Union[Ldict, Aux]":
        """Update the dictionary with the key/value pairs from other, overwriting existing keys. Return self.
        Usage:
        >>> from ldict import ldict
        >>> a = ldict(x=123)
        >>> print(a)
        {
            "id": "60jQU3QwRj32mVemRtQ5wydSMS8whbv5EGQOTZni8sy",
            "x": 123,
            "id_x": "<hidden field>"
        }
        >>> b = ldict(y="some text")
        >>> print(b)
        {
            "id": "MUDScy6oRARmYxSUOBTy6vWpxn9WoTEOksUhxsOVK6q",
            "y": "some text",
            "id_y": "<hidden field>"
        }
        >>> print(b.update(a))
        {
            "id": "SUwt71XkstUpLT7Gq4u43uAIKFITW59Tz8v6RSCDSzo",
            "y": "some text",
            "x": 123,
            "id_*": "<2 hidden fields>"
        }
        """
        from ldict import Ldict
        kwds.update(other)
        ids = {}
        for field, value in kwds.items():
            if not field.startswith("id_") and field != "id":
                if field in self.data:
                    raise Exception(f"Conflict in field {field}")
                idk = f"id_{field}"
                self[field] = value
                if idk in kwds:
                    ids[idk] = kwds[idk]
                    if isinstance(other, Ldict):
                        self.hashes[field] = other.hashes[field]
                        self.keepblob = other.keepblob
                        if field in other.blobs:
                            self.blobs[field] = other.blobs[field]
        self.data.update(ids)
        return self
