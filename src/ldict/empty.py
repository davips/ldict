from ldict.core import Ldict


class Empty:
    def __rshift__(self, other):
        """
        Usage
        >>> d = ø >> {"x": 2}
        >>> d.show(colored=False)
        >>> d >>= {"y": 2}
        >>> d.show(colored=False)

        >>> d >>= (lambda x: {"x": x**2})
        >>> d.show(colored=False)

        """
        return Ldict(other)
