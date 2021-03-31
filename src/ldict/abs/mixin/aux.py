import json
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
        108990846591764296187947743094879269859
        """
        return self.hash.n

    @property
    def id(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124).id
        '0000000000000000000002Uir4UFhytZSbfZqV8rALj'
        """
        return self.hash.id

    @property
    def ids(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124).ids
        {'x': '0000000000000000000002Uir4UFhytZSbfZqV8rALj'}
        """
        return {f: h.id for f, h in self.hashes.items()}

    @property
    def all(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> print(ldict(x=134124, y= 56).all)
        {
            "id": "\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;203m\x1b[1mt\x1b[0m\x1b[38;5;173m\x1b[1mT\x1b[0m\x1b[38;5;167m\x1b[1mH\x1b[0m\x1b[38;5;167m\x1b[1ma\x1b[0m\x1b[38;5;173m\x1b[1mz\x1b[0m\x1b[38;5;167m\x1b[1mK\x1b[0m\x1b[38;5;203m\x1b[1m6\x1b[0m\x1b[38;5;167m\x1b[1mb\x1b[0m\x1b[38;5;209m\x1b[1mE\x1b[0m\x1b[38;5;167m\x1b[1m5\x1b[0m\x1b[38;5;209m\x1b[1mU\x1b[0m\x1b[38;5;203m\x1b[1mI\x1b[0m\x1b[38;5;167m\x1b[1m1\x1b[0m\x1b[38;5;203m\x1b[1mQ\x1b[0m\x1b[38;5;203m\x1b[1mN\x1b[0m\x1b[38;5;167m\x1b[1mP\x1b[0m\x1b[38;5;203m\x1b[1mo\x1b[0m\x1b[38;5;203m\x1b[1mJ\x1b[0m\x1b[38;5;203m\x1b[1mc\x1b[0m\x1b[38;5;173m\x1b[1mD\x1b[0m\x1b[38;5;203m\x1b[1mI\x1b[0m",
            "x": 134124,
            "id_x": "\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;97m\x1b[1m2\x1b[0m\x1b[38;5;98m\x1b[1mU\x1b[0m\x1b[38;5;62m\x1b[1mi\x1b[0m\x1b[38;5;63m\x1b[1mr\x1b[0m\x1b[38;5;61m\x1b[1m4\x1b[0m\x1b[38;5;98m\x1b[1mU\x1b[0m\x1b[38;5;97m\x1b[1mF\x1b[0m\x1b[38;5;98m\x1b[1mh\x1b[0m\x1b[38;5;63m\x1b[1my\x1b[0m\x1b[38;5;99m\x1b[1mt\x1b[0m\x1b[38;5;98m\x1b[1mZ\x1b[0m\x1b[38;5;62m\x1b[1mS\x1b[0m\x1b[38;5;62m\x1b[1mb\x1b[0m\x1b[38;5;62m\x1b[1mf\x1b[0m\x1b[38;5;98m\x1b[1mZ\x1b[0m\x1b[38;5;63m\x1b[1mq\x1b[0m\x1b[38;5;98m\x1b[1mV\x1b[0m\x1b[38;5;61m\x1b[1m8\x1b[0m\x1b[38;5;63m\x1b[1mr\x1b[0m\x1b[38;5;97m\x1b[1mA\x1b[0m\x1b[38;5;62m\x1b[1mL\x1b[0m\x1b[38;5;62m\x1b[1mj\x1b[0m",
            "y": 56,
            "id_y": "\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;59m\x1b[1m6\x1b[0m\x1b[38;5;65m\x1b[1mB\x1b[0m\x1b[38;5;61m\x1b[1mo\x1b[0m\x1b[38;5;66m\x1b[1mS\x1b[0m\x1b[38;5;66m\x1b[1mj\x1b[0m\x1b[38;5;66m\x1b[1ml\x1b[0m\x1b[38;5;66m\x1b[1mQ\x1b[0m\x1b[38;5;66m\x1b[1mU\x1b[0m\x1b[38;5;59m\x1b[1m6\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;240m\x1b[1mH\x1b[0m\x1b[38;5;66m\x1b[1ml\x1b[0m\x1b[38;5;61m\x1b[1mq\x1b[0m\x1b[38;5;65m\x1b[1m8\x1b[0m\x1b[38;5;67m\x1b[1mz\x1b[0m\x1b[38;5;241m\x1b[1mJ\x1b[0m\x1b[38;5;61m\x1b[1mn\x1b[0m\x1b[38;5;61m\x1b[1mm\x1b[0m\x1b[38;5;66m\x1b[1mi\x1b[0m\x1b[38;5;65m\x1b[1m9\x1b[0m\x1b[38;5;243m\x1b[1mR\x1b[0m\x1b[38;5;65m\x1b[1m8\x1b[0m"
        }
        """
        return self.__repr__(all=True)

    def show(self):
        """
        Usage:
        >>> from ldict import ldict
        >>> ldict(x=134124, y= 56).show()
        {
            "id": "\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;167m\x1b[1m0\x1b[0m\x1b[38;5;203m\x1b[1mt\x1b[0m\x1b[38;5;173m\x1b[1mT\x1b[0m\x1b[38;5;167m\x1b[1mH\x1b[0m\x1b[38;5;167m\x1b[1ma\x1b[0m\x1b[38;5;173m\x1b[1mz\x1b[0m\x1b[38;5;167m\x1b[1mK\x1b[0m\x1b[38;5;203m\x1b[1m6\x1b[0m\x1b[38;5;167m\x1b[1mb\x1b[0m\x1b[38;5;209m\x1b[1mE\x1b[0m\x1b[38;5;167m\x1b[1m5\x1b[0m\x1b[38;5;209m\x1b[1mU\x1b[0m\x1b[38;5;203m\x1b[1mI\x1b[0m\x1b[38;5;167m\x1b[1m1\x1b[0m\x1b[38;5;203m\x1b[1mQ\x1b[0m\x1b[38;5;203m\x1b[1mN\x1b[0m\x1b[38;5;167m\x1b[1mP\x1b[0m\x1b[38;5;203m\x1b[1mo\x1b[0m\x1b[38;5;203m\x1b[1mJ\x1b[0m\x1b[38;5;203m\x1b[1mc\x1b[0m\x1b[38;5;173m\x1b[1mD\x1b[0m\x1b[38;5;203m\x1b[1mI\x1b[0m",
            "x": 134124,
            "id_x": "\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;61m\x1b[1m0\x1b[0m\x1b[38;5;97m\x1b[1m2\x1b[0m\x1b[38;5;98m\x1b[1mU\x1b[0m\x1b[38;5;62m\x1b[1mi\x1b[0m\x1b[38;5;63m\x1b[1mr\x1b[0m\x1b[38;5;61m\x1b[1m4\x1b[0m\x1b[38;5;98m\x1b[1mU\x1b[0m\x1b[38;5;97m\x1b[1mF\x1b[0m\x1b[38;5;98m\x1b[1mh\x1b[0m\x1b[38;5;63m\x1b[1my\x1b[0m\x1b[38;5;99m\x1b[1mt\x1b[0m\x1b[38;5;98m\x1b[1mZ\x1b[0m\x1b[38;5;62m\x1b[1mS\x1b[0m\x1b[38;5;62m\x1b[1mb\x1b[0m\x1b[38;5;62m\x1b[1mf\x1b[0m\x1b[38;5;98m\x1b[1mZ\x1b[0m\x1b[38;5;63m\x1b[1mq\x1b[0m\x1b[38;5;98m\x1b[1mV\x1b[0m\x1b[38;5;61m\x1b[1m8\x1b[0m\x1b[38;5;63m\x1b[1mr\x1b[0m\x1b[38;5;97m\x1b[1mA\x1b[0m\x1b[38;5;62m\x1b[1mL\x1b[0m\x1b[38;5;62m\x1b[1mj\x1b[0m",
            "y": 56,
            "id_y": "\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;59m\x1b[1m6\x1b[0m\x1b[38;5;65m\x1b[1mB\x1b[0m\x1b[38;5;61m\x1b[1mo\x1b[0m\x1b[38;5;66m\x1b[1mS\x1b[0m\x1b[38;5;66m\x1b[1mj\x1b[0m\x1b[38;5;66m\x1b[1ml\x1b[0m\x1b[38;5;66m\x1b[1mQ\x1b[0m\x1b[38;5;66m\x1b[1mU\x1b[0m\x1b[38;5;59m\x1b[1m6\x1b[0m\x1b[38;5;239m\x1b[1m0\x1b[0m\x1b[38;5;240m\x1b[1mH\x1b[0m\x1b[38;5;66m\x1b[1ml\x1b[0m\x1b[38;5;61m\x1b[1mq\x1b[0m\x1b[38;5;65m\x1b[1m8\x1b[0m\x1b[38;5;67m\x1b[1mz\x1b[0m\x1b[38;5;241m\x1b[1mJ\x1b[0m\x1b[38;5;61m\x1b[1mn\x1b[0m\x1b[38;5;61m\x1b[1mm\x1b[0m\x1b[38;5;66m\x1b[1mi\x1b[0m\x1b[38;5;65m\x1b[1m9\x1b[0m\x1b[38;5;243m\x1b[1mR\x1b[0m\x1b[38;5;65m\x1b[1m8\x1b[0m"
        }
        """
        return print(self.all)

    @property
    def perm(self):
        """
        For new data, it is always the identity permutation.
        Usage:
        >>> from ldict import ldict
        >>> a = ldict(x=134124)
        >>> a.perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> (a + a).perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> b = a + ldict(y=134124)
        >>> b.perm
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        >>> f = lambda x: {'z': x ** 2}
        >>> print(b >> f)
        {
            "id": "DJCI4NHm3GUzL4KQt7W3dWh3JkAGSMz5Ttx9lzoNnMQ",
            "x": 134124,
            "y": 134124,
            "z": "<unevaluated lazy field>",
            "id_*": "<hidden fields>"
        }
        """
        return self.hash.perm

    def __repr__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if callable(v):
                dic[k] = "<unevaluated lazy field>"
            if not all and k.startswith("id_"):
                del dic[k]
        if not all:
            dic["id_*"] = "<hidden fields>"
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
        ('0000000000000000000002Uir4UFhytZSbfZqV8rALj', '0000000000000000000004BL8Zqg8riPMdIaO6eMAC9')
        >>> print(a + b)
        {
            "id": "0000000000000000000006g3zeKvqqbypEyAEbnDKXs",
            "x": 134124,
            "y": 542542,
            "id_*": "<hidden fields>"
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

    def __str__(self, all=False):
        dic = self.data.copy()
        for k, v in self.data.items():
            if not all and k.startswith("id_"):
                del dic[k]
            elif callable(v):
                dic[k] = "<unevaluated lazy field>"
        dic["id_*"] = "<hidden fields>"
        return json.dumps(dic, indent=4)

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
            "id": "0000000000000000000006pnWvaKVQbhfaIl82A1WD6",
            "x": 123,
            "id_*": "<hidden fields>"
        }
        >>> b = ldict(y="some text")
        >>> print(b)
        {
            "id": "00000000000000000000001Q5vqu6zuQ864lVfx25Vw",
            "y": "some text",
            "id_*": "<hidden fields>"
        }
        >>> print(b.update(a))
        {
            "id": "0000000000000000000006rDcrREcQW7ngNWdi73bj2",
            "y": "some text",
            "x": 123,
            "id_*": "<hidden fields>"
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
